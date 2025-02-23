# FIVE-STRING BASS FRETBOARD LAYOUT (Standard tuning)
# | 0   | 1    | 2    | 3    | 4    |
# | --- | ---- | ---- | ---- | ---- |
# | G2  | #/b | A2   | #/b | B2   |
# | D2  | #/b | E2   | F2   | #/b |
# | A1  | #/b | B1   | C2   | #/b |
# | E1  | F1   | #/b | G1   | #/b |
# | B0  | C1   | #/b | D1   | #/b |
#
# CURRENT NOTEMAPPING FOR BASS:
# | 0              | 1                 | 2                | 3              |
# | -------------- | ----------------- | ---------------- | -------------- |
# | Open inventory | Open menu         | Use/Interact     |                |
# | Jump to back   | Previous in queue | Next in queue    | Jump to front  |
# | Primary Attack | Special Attack    | Secondary Attack | Dash/roll      |
# | Forward-Left   | Forward-Right     | Backward-Left    | Backward-Right |
# | Forward        | Left              | Right            | Backward       |
#
# TODO: 
#   1. Have program generate a notemap if none exist

from __future__ import annotations
import subprocess, os, platform, json, glob  # For saving and editing notemaps
import keybinds as kb


class NoteMap:
    notemaps = []
    range_error = ValueError("Variable 'note_range' must be a list of 2 notes in [Note][Octave] format between A0 and C8")

    # If weird inputs start happening, double check this list for correct scale order
    # TODO: Add support for proper scales
    chromatic_scale = ["A0", "B0", "C1", "C#1", "D1", "D#1",
                        "E1", "F1", "F#1", "G1", "G#1", "A1",
                        "A#1", "B1", "C2", "C#2", "D2", "D#2", 
                        "E2", "F2", "F#2", "G2", "G#2", "A2",
                        "A#2", "B2", "C3", "C#3", "D3", "D#3",
                        "E3", "F3", "F#3", "G3", "G#3", "A3",
                        "A#3", "B3", "C4", "C#4", "D4", "D#4",
                        "E4", "F4", "F#4", "G4", "G#4", "A4",
                        "A#4", "B4", "C5", "C#5", "D5", "D#5",
                        "E5", "F5", "F#5", "G5", "G#5", "A5",
                        "A#5", "B5", "C6", "C#6", "D6", "D#6",
                        "E6", "F6", "F#6", "G6", "G#6", "A6",
                        "A#6", "B6", "C7", "C#7", "D7", "D#7",
                        "E7", "F7", "F#7", "G7", "G#7", "A7",
                        "A#7", "B7", "C8"]

    def edit_notemap(self) -> None:
        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", self.path))
        elif platform.system() == "Windows":  # Windows
            os.startfile(self.path)
        else:  # linux variants
            subprocess.call(("xdg-open", self.path))

    def write_notemap(self) -> None:
        json_content = {
            "type": "notemap",
            "idx": self.idx,
            "default": self.default,
            "instrument": self.instr,
            "game": self.game,
            "notemap": self.notemap,
        }

        with open(self.path + self.name + ".json", "w") as f:
            json.dump(json_content, f, indent=4)

    def update_notemap(self, notemap: NoteMap) -> None:
        self.notemap = notemap

    def set_note_range(self, new_note_range: list) -> None:
        is_valid = self.valid_note_range(new_note_range)

        if is_valid[0]:
            if new_note_range[0] > new_note_range[1]:
                self.note_range = [new_note_range[1], new_note_range[0]]
            else:
                self.note_range = [new_note_range[0], new_note_range[1]]
        else:
            raise is_valid[1]

    # TODO: Check that note_range is no more than a 1:1 with the note->action mapping
    # TODO: Support more than chromatic scale
    def valid_note_range(self, note_range: list):
        is_valid = True
        if len(note_range) != 2:
            self.range_error = ValueError(
                "Variable 'note_range' must be a list of 2 notes in [Note][Octave] format"
            )
            is_valid = False

        for i in range(len(note_range)):
            if note_range[i] not in self.chromatic_scale:
                self.range_error = ValueError(
                    "Variable 'note_range' must be a list of 2 notes and be between A0 and C8"
                )
                is_valid = False

        return (is_valid, self.range_error)

    def add_notemap(self, notemap):
        """
        Adds a notemap to this instrument.
        """

        if isinstance(notemap, NoteMap):
            self.notemaps.append(notemap)
        else:
            raise TypeError("Variable 'notemap' must be of type NoteMap")

    def remove_notemap(self, notemap):
        """
        Removes a notemap from this instrument.
        """

        if notemap in self.notemaps:
            self.notemaps.remove(notemap)
        else:
            raise ValueError("Variable 'notemap' must be a notemap of this instrument")

    def set_default_notemap(self, notemap):
        """
        Sets the default notemap for this instrument.
        If the given notemap is not already in the list of notemaps, it will be added.
        """

        if notemap in self.notemaps:
            self.default_notemap = notemap
        elif isinstance(notemap, NoteMap):
            self.notemaps.append(notemap)
            self.default_notemap = notemap
        else:
            raise TypeError("Variable 'notemap' must be of type NoteMap")

    def __init__(self, note_range, idx, instr, game) -> None:
        self.name = "notemap_" + str(idx)

        valid = self.valid_note_range(note_range)
        if valid[0]:
            self.set_note_range(note_range)
        else:
            raise valid[1]

        self.game = game
        self.path = os.path.join(os.getcwd(), "instruments", instr, self.game)
        self.keybinds = {}
        self.notemap = {}
        self.notemap_idx = None

        notemap_dir = os.path.join(self.path, self.name)
        configs = [x for x in os.listdir(notemap_dir) if not x.startswith(".")]
        for config in configs:
            if ".json" in config:
                with open(os.path.join(notemap_dir, config), "r") as f:
                    data = json.load(f)
                    if data["type"] == "keybind":
                        # TODO: Verify keybind validity before adding it to dict
                        self.keybinds[config.split(".")[0]] = kb.Keybind(binding=data["keybinds"], name=config, default=data["default"])
                    elif data["type"] == "notemap":
                        self.notemap[self.game] = data["notemap"]
                        self.instr = data["instrument"]
                        self.default = data["default"]
                        self.game = data["game"]
                        self.notemap_idx = data["idx"]


        if not self.keybinds:
            raise ValueError(f'No keybinds found in folder "{notemap_dir}"')

    def __str__(self):
        return os.path.join(self.instr.path, self.game, self.name)

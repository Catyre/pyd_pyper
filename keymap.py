# FIVE-STRING BASS FRETBOARD LAYOUT (Standard tuning)
# | 0   | 1    | 2    | 3    | 4    |
# | --- | ---- | ---- | ---- | ---- |
# | G2  | \#/b | A2   | \#/b | B2   |
# | D2  | \#/b | E2   | F2   | \#/b |
# | A1  | \#/b | B1   | C2   | \#/b |
# | E1  | F1   | \#/b | G1   | \#/b |
# | B0  | C1   | \#/b | D1   | \#/b |
# 
# CURRENT KEYMAPPING FOR BASS:
# | 0              | 1                 | 2                | 3              |
# | -------------- | ----------------- | ---------------- | -------------- |
# | Open inventory | Open menu         | Use/Interact     |                |
# | Jump to back   | Previous in queue | Next in queue    | Jump to front  |
# | Primary Attack | Special Attack    | Secondary Attack | Dash/roll      |
# | Forward-Left   | Forward-Right     | Backward-Left    | Backward-Right |
# | Forward        | Left              | Right            | Backward       |

from __future__ import annotations
import subprocess, os, platform # For saving and editing keymaps

class KeyMap:
    range_error = ValueError('variable \'note_range\' must be a list of 2 notes in [Note][Octave] format between A0 and C8')

    # If weird inputs start happening, double check this list for correct scale order
    # TODO: Add support for proper scales
    chromatic_scale = ['A0', 'B0', 'C1', 'C#1', 'D1', 'D#1', 'E1', 'F1', 
                        'F#1','G1', 'G#1', 'A1', 'A#1', 'B1', 'C2', 'C#2',
                        'D2', 'D#2', 'E2', 'F2', 'F#2', 'G2', 'G#2', 'A2', 
                        'A#2', 'B2', 'C3', 'C#3', 'D3', 'D#3', 'E3', 'F3', 
                        'F#3', 'G3', 'G#3', 'A3', 'A#3', 'B3', 'C4', 'C#4', 
                        'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 
                        'A#4', 'B4', 'C5', 'C#5', 'D5', 'D#5', 'E5', 'F5',
                        'F#5', 'G5', 'G#5', 'A5', 'A#5', 'B5', 'C6', 'C#6',
                        'D6', 'D#6', 'E6', 'F6', 'F#6', 'G6', 'G#6', 'A6',
                        'A#6', 'B6', 'C7', 'C#7', 'D7', 'D#7', 'E7', 'F7',
                        'F#7', 'G7', 'G#7', 'A7', 'A#7', 'B7', 'C8']

    def generate_keymap(self, keys: list, notes: list) -> dict:
        self.keymap = dict()

        self.keymap[note] = [keys[self.chromatic_scale.index(note)] for note in notes]

        return self.keymap


    # Match keybinds to input
    # TODO: Pass instrument as command line argument and use that to determine which keymap to use
    def match_keybinds(self) -> dict:
        # Dictionary to map notes to keybinds of the current instrument's keymap
        self.note_to_key = {}

        for keymap_elem in keymappings[instrument].items():
            note_to_key[keymap_elem[0]] = generic_inputs[keymap_elem[1]]

        return note_to_key


    def edit_keymap(self) -> None:
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', self.path))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(self.path)
        else:                                   # linux variants
            subprocess.call(('xdg-open', self.path))


    def save_keymap(self) -> None:
        with open(self.path + self.name + '.txt', 'w') as f:
            # Will need this to be more sophisticated later
            f.write(self.keymap)


    def update_keymap(self, keymap: KeyMap) -> None:
        self.keymap = keymap


    def set_note_range(self, new_note_range: list) -> None:
        is_valid = valid_note_range(new_note_range)

        if is_valid[0]:
            if new_note_range[0] > new_note_range[1]:
                self.note_range = [new_note_range[1], new_note_range[0]]
            else:
                self.note_range = [new_note_range[0], new_note_range[1]]
        else:
            raise is_valid[1]

    # TODO: Check that note_range is no more than a 1:1 with the action->key mapping
    # TODO: Support more than chromatic scale
    def valid_note_range(self, note_range: list) -> bool:
        is_valid = True
        if len(note_range) != 2:
            range_error = ValueError('variable \'note_range\' must be a list of 2 notes in [Note][Octave] format')
            is_valid = False

        for i in range(len(note_range)):
            if note_range[i] not in chromatic_scale:
                range_error = ValueError('variable \'note_range\' must be a list of 2 notes and be between A0 and C8')
                is_valid = False 

        return (is_valid, range_error)
 
    def __init__(self, path: str, note_range: list) -> None:
        valid = self.valid_note_range(note_range)
        self.set_note_range(note_range)

        self.path = os.path.join(path, "keymaps")
        self.generic_mvmt_inputs = {'forward': 'w',
                                    'backward': 's',
                                    'left': 'a',
                                    'right': 'd',
                                    'forward-left': 'w+a',
                                    'forward-right': 'w+d',
                                    'backward-left': 's+a',
                                    'backward-right': 's+d'}

        self.generic_combat_inputs = {'primary': 'left-click',
                                        'secondary': 'right-click',
                                        'special': 'e',
                                        'dash': 'space'}

        self.generic_menu_inputs = {'inventory': '', 
                                    'menu': 'esc',
                                    'queue_front': '',
                                    'queue_back': '',
                                    'queue_next': '',
                                    'queue_prev': '', 
                                    'use': 'r'}

        self.generic_inputs = {}
        self.generic_inputs.update(self.generic_mvmt_inputs)
        self.generic_inputs.update(self.generic_combat_inputs)
        self.generic_inputs.update(self.generic_menu_inputs)


        self.keymap = {}

        self.keymap[note] = [keys[self.chromatic_scale.index(note)] for note in notes]
        self.keymap = {note:self.generic_inpus[] for (note, key[note]) in zip()}

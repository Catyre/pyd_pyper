from __future__ import annotations
import subprocess, os, platform # For saving and editing notemaps

class Keybind:
    # Match keybinds to input
    # TODO: Pass instrument as command line argument and use that to determine which notemap to use
    def match_keybinds(self) -> dict:
        # Dictionary to map notes to keybinds of the current instrument's notemap
        self.note_to_key = {}

        for notemap_elem in notemappings[instrument].items():
            note_to_key[notemap_elem[0]] = generic_inputs[notemap_elem[1]]

        return note_to_key


    def edit_keybind(self) -> None:
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', self.path))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(self.path)
        else:                                   # linux variants
            subprocess.call(('xdg-open', self.path))


    def save_keybind(self) -> None:
        with open(self.path + self.name + '.json', 'w') as f:
            # Will need this to be more sophisticated later
            f.write(self.keybind)


    def update_keybind(self, keybind) -> None:
        self.keybind = keybind
 

    def __init__(self, binding, name, default) -> None:
        if not name:
            self.name = 'keybind_' + str(len(keybinds))
        else:
            self.name = name
        
        self.keybind = binding

    def __getitem__(self, key):
        return self.keybind[key]

import os
import keymap as km

# Class to represent an instrument, which contains data about the keymap(s), ranges, and other instrument-specific data
class Instrument:
    all_instruments = [] # List of all instruments

    def __init__(self, name="", note_range=["A0", "C8"], path=os.getcwd()):
        self.name = name
        self.path = os.path.join(path, "instruments", name) # .../pyd_pyper/instruments/[name]
        self.default_keymap = km.KeyMap(path=os.path.join(self.path, "keymaps"), note_range=note_range) # path=.../pyd_pyper/instruments/[name]/keymaps
        # Keymaps should be added if there are any in the directory
        self.keymaps = [self.default_keymap]
        all_instruments.append(self)


    def __str__(self):
        return self.name


    def __repr__(self):
        return self.name


    def __eq__(self, other):
        if self.name == other.name:
            if [x for x in self.keymaps] == [x for x in other.keymaps]:
                return True


    def get_instruments(self):
        return instruments


    def add_keymap(self, keymap):
        """
        Adds a keymap to this instrument.
        """

        if isinstance(keymap, km.KeyMap):
            self.keymaps.append(keymap)
        else:
            raise TypeError('variable \'keymap\' must be of type KeyMap')


    def remove_keymap(self, keymap):
        """
        Removes a keymap from this instrument.
        """

        if keymap in self.keymaps:
            self.keymaps.remove(keymap)
        else:
            raise ValueError('variable \'keymap\' must be a keymap of this instrument')


    def set_default_keymap(self, keymap):
        """
        Sets the default keymap for this instrument.  
        If the given keymap is not already in the list of keymaps, it will be added.
        """

        if keymap in self.keymaps:
            self.default_keymap = keymap
        elif isinstance(keymap, km.KeyMap):
            self.keymaps.append(keymap)
            self.default_keymap = keymap
        else:
            raise TypeError('variable \'keymap\' must be of type KeyMap')

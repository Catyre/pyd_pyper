import os
import notemap as nm
import json


# Class to represent an instrument, which contains data about the notemap(s), ranges, and other instrument-specific data
class Instrument:
    all_instruments = [
        x for x in os.listdir(os.path.join(os.getcwd(), "instruments"))
    ]  # List of all instruments

    def __init__(self, name, game, note_range=["A0", "C8"]):
        self.notemaps = {}
        self.name = name
        self.path = os.path.join(os.getcwd(), "instruments", name)  # .../pyd_pyper/instruments/[name]
        self.note_range = note_range
        self.game = game

        # Check the instrument's folder for existing notemaps and keybinds
        self.games = [x for x in os.listdir(self.path) if not x.startswith(".")]  # List of all games
        if len(self.games) > 0:
            for poss_games in self.games:
                if self.game == poss_games:
                    self.notemaps[self.game] = []
                    num_notemaps = len([x for x in os.listdir(os.path.join(self.path, self.game)) if not x.startswith(".")])
                    for idx in range(num_notemaps):
                        self.notemaps[self.game].append(nm.NoteMap(self.note_range, idx+1, self.name, self.game))
        else:
            raise ValueError(f'No games found in folder "{self.path}"')

        Instrument.all_instruments.append(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name and [x for x in self.notemaps] == [
            x for x in other.notemaps
        ]

    def get_instruments(self):
        return Instrument.all_instruments

import os
import notemap as nm
import keybinds as kb
import json

# Class to represent an instrument, which contains data about the notemap(s), ranges, and other instrument-specific data
class Instrument:
    all_instruments = [x for x in os.listdir(os.path.join(os.getcwd(), "instruments"))] # List of all instruments

    def __init__(self, name, note_range=["A0", "C8"]):
        self.notemaps = {}
        self.name = name
        self.path = os.path.join(os.getcwd(), "instruments", name) # .../pyd_pyper/instruments/[name]

        # Check the instrument's folder for existing notemaps and keybinds
        self.games = [x for x in os.listdir(self.path) if not x.startswith('.')] # List of all games
        if len(self.games) > 0:
            for game in self.games:
                game_dir = os.path.join(self.path, game)
                for notemap in os.listdir(game_dir):
                    if not notemap.startswith('.'):
                        try:
                            with open(os.path.join(game_dir, notemap, 'notemap.json'), 'r') as f:
                                data = json.load(f)
                                self.notemaps[game] = nm.NoteMap(note_range=note_range, name=notemap, mapping=data['notemap'], game=game, default=data['default'], instr=self)
                        except FileNotFoundError:
                            print(f"Could not find notemap.json in folder \"{os.path.join(game_dir, notemap)}\"")
        else:
            raise ValueError(f"No games found in folder \"{self.path}\"")

        Instrument.all_instruments.append(self)


    def __str__(self):
        return self.name


    def __repr__(self):
        return self.name


    def __eq__(self, other):
        return self.name == other.name and [x for x in self.notemaps] == [x for x in other.notemaps]


    def get_instruments(self):
        return Instrument.all_instruments

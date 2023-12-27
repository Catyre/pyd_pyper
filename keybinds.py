from pynput.keyboard import Key, Controller

keyboard = Controller()
def parse_note_input(note, keymap):
    keyboard.tap(keymap[note])

    pass


def add_instrument():
    pass

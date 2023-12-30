# Default python libraries
import sys, os, glob, argparse, time

# Pyd Pyper libraries
import keybinds as kb
import instrument
import notemap as nm
import audio_handler as ah

def list_options(options):
    selection = None
    choices = "\n"

    if len(options) > 1:
        for idx, option in enumerate(options): choices += f"    {idx}. {option}\n"
        while selection not in range(len(options)):
            selection = int(input(f"\nOptions (\"*[option]\" = default):{choices}Choose one number: "))
    elif len(options) == 1:
        selection = 0
    else:
        print("No selections found.  Exiting...")
        sys.exit()

    return options[selection]


if __name__ == "__main__":
    global unique_note_count
    handler = ah.AudioHandler() # Instantiate audio handler

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Make keybinds for analog instruments.')
    parser.add_argument('-i', '--input', default=None, help='Set the desired input device.')
    parser.add_argument('--instr', default=None, help='Set the desired instrument to use.')
    parser.add_argument('-g', '--game', default=None, help='Set the desired game to use notemaps for.')
    parser.add_argument('-n', '--notemap', default=None, help='Set the desired notemap.')
    parser.add_argument('-k', '--keybind', default=None, help='Set the desired keybind for the given notemap.')

    args = parser.parse_args()

    input_device = args.input
    instr = args.instr
    game = args.game
    notemap = args.notemap
    keybind = args.keybind

    # TODO: Prompt user to make these files if none are found
    device_choices = handler.get_devices()
    if input_device is None:
        print('What input device would you like to use?')
        input_device = list_options([choice.get('name') for choice in device_choices])
    if instr is None:
        poss_choices = [x for x in os.listdir(os.path.join(os.getcwd(), "instruments")) if not  x.startswith('.')]
        print('\nWhat instrument configuration would you like to use?')
        instr = list_options(poss_choices)
    if game is None:
        poss_choices = [x for x in os.listdir(os.path.join(os.getcwd(), "instruments", instr)) if not  x.startswith('.')]
        print('\nWhat game would you like to use Pyd Pyper for?')
        game = list_options(poss_choices)
    if notemap is None:
        poss_choices = [x for x in os.listdir(os.path.join(os.getcwd(), "instruments", instr, game)) if not  x.startswith('.')]
        print(f'\nWhat notemap would you lke to use for {game}?')
        notemap = list_options(poss_choices)
    if keybind is None:
        poss_choices = [x for x in os.listdir(os.path.join(os.getcwd(), "instruments", instr, game, notemap)) if not  x.startswith('.') and x != 'notemap.txt']
        print(f'\nWhat keybind would you like to use for {game}: {notemap}?')
        keybind = list_options(poss_choices)

    # We need to turn the user's input into the actual object
    instr = instrument.Instrument(instr, note_range=['D1', 'B2'])
    notemap = instr.notemaps[game][notemap]
    keybinds = notemap.keybinds[keybind]
    device_idx = [i for i, device in enumerate(device_choices) if device.get('name') == input_device][0]
    input_device = device_choices[device_idx]
    unique_note_count = dict() # Dictionary to store unique notes and their occurences

    handler.use_instrument(instr)
    handler.start(device=input_device)
    while handler.is_active():
        time.sleep(0.4)
        unique_note_count = handler.unique_note_count
        if unique_note_count:
            # Find the key with the highest value in the dictionary (note with highest occurence)
            note_guess = max(unique_note_count, key=unique_note_count.get)

            print("Closest note to input: " + note_guess)
            try:
                key = keybinds[notemap.mapping[note_guess]]
                #print(f"Action: {notemap.mapping[note_guess]}\nKey: {key}")
            except KeyError:
                print(f"Note {note_guess} not found in notemap")

        handler.reset_unique_note_count()

    handler.stop()

import pyaudio, librosa
import numpy as np
import time
import argparse
import sys, os, glob
import keybinds as kb
import instrument
import notemap as nm

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

#Convert PCM signal to floating point with a range from -1 to 1. Use dtype='float32' for single precision.
def pcm2float(sig, dtype='float32'):
    sig = np.asarray(sig)
    if sig.dtype.kind not in 'iu':
        raise TypeError("'sig' must be an array of integers")
    dtype = np.dtype(dtype)
    if dtype.kind != 'f':
        raise TypeError("'dtype' must be a floating point type")

    i = np.iinfo(sig.dtype)
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max
    return (sig.astype(dtype) - offset) / abs_max


# byte -> int16(PCM_16) -> float32
def byte_to_float(byte):
    return pcm2float(np.frombuffer(byte,dtype=np.int16), dtype='float32')

# Cleaning the audio seems to fuck up the analysis; investigate further
def callback(in_data, frame_count, time_info, status):
    global unique_note_count
    in_data_dec = byte_to_float(in_data) # Convert audio byte data to float data
    #print("Raw data: ", in_data)
    #print("Decoded data: ", in_data_dec)
    audio = np.nan_to_num(in_data_dec) # Convert NaNs to 0s
    #audio = librosa.load("G2.wav")
    #print(type(audio))

    # Remove noise from audio data if within precision limit
    #for i in range(len(audio)):
    #    if audio[i] < PREC_LIMIT and audio[i] > -1 * PREC_LIMIT:
    #        audio[i] = 0 also

    pitches = librosa.yin(y=audio, frame_length=CHUNK, fmin=librosa.note_to_hz("G1"), fmax=librosa.note_to_hz("A3"))
    print(pitches)
    #pitches, magnitudes = librosa.piptrack(y=audio, sr=rate, fmin=librosa.note_to_hz("B1"), fmax=librosa.note_to_hz("F4"))
    #note = librosa.hz_to_note(pitches)
    geo_mean = np.exp(np.mean(np.log(pitches)))

    #if (geo_mean < 90):
    #    print("Below range")
    #elif (geo_mean > 110):
    #    print("Above range")
    #else:
    #    print("In range")

    note = librosa.hz_to_note(geo_mean)

    if unique_note_count.get(note) is None:
        unique_note_count[note] = 1
    else:
        unique_note_count[note] += 1

    return in_data, pyaudio.paContinue


if __name__ == "__main__":
    global unique_note_count
    CHUNK = 1024
    FORMAT = pyaudio.paInt16 # .wav format dtype
    PREC_LIMIT = 1e-8

    # Instantiate PyAudio and initialize PortAudio system resources
    p = pyaudio.PyAudio()

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
    if input_device is None:
        device_choices = [p.get_device_info_by_host_api_device_index(0, i).get('name') for i in range(p.get_host_api_info_by_index(0).get('deviceCount'))]
        print('What input device would you like to use?')
        input_device = list_options(poss_choices)
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
    instr = instrument.Instrument(instr)
    print(instr)


    # Set default values (will be changed if not using defaults)
    device_idx = device_choices.index(input_device)
    channels = input_device.get('maxInputChannels')
    rate = int(input_device.get('defaultSampleRate'))

    stream = p.open(format=FORMAT,channels=channels,
                    rate=rate,
                    input_device_index=device_idx,
                    input=True,
                    stream_callback=callback)

    unique_note_count = dict() # Dictionary to store unique notes and their occurences

    stream.start_stream()
    print('Recording...')
    while stream.is_active():
        time.sleep(0.1) 

        if unique_note_count:
            # Find the key with the highest value in the dictionary (note with highest occurence)
            note_guess = max(unique_note_count, key=unique_note_count.get)

        print("Closest note to input: " + note_guess)
        #key = 
        

        unique_note_count = dict() # Reset dictionary

    stream.stop_stream()
    stream.close()
    p.terminate()

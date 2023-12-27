import pyaudio, librosa
import numpy as np
import time
import argparse
import sys
import keybinds as kb
import instruments as inst
import keymap as km

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
    # Instantiate PyAudio and initialize PortAudio system resources
    p = pyaudio.PyAudio()
    numdev = p.get_host_api_info_by_index(0).get('deviceCount')
    dummy_inst = inst.Instrument("dummy", ['A0', 'C8'])
    curr_inst_choices = dummy_inst.get_instruments()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Make keybinds for analog instruments.')
    parser.add_argument('-i', '--input', dest='input_device', default=p.get_default_input_device_info().get('name'),
                        help='Set the desired input device.  If not used, the system\'s default input device will be used.')
    parser.add_argument('-l', '--list', action='store_true',
                        help='List the available input devices at the time of running this program.  If used, the program will exit after displaying the list of input devices.')
    parser.add_argument('--inst', dest='instrument', choices=['bass'],
                        help='Set the desired instrument to use.')
    args = parser.parse_args()

    # List the available input devices if the -l flag is used.  This will also exit the program.
    if args.list:
        for i in range(numdev):
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

        sys.exit()

    #

    # Change this variable to the name of your desired input device
    input_device = args.input
    found_device = False

    #pitches = None
    #audio = None
    #geo_mean = None

    global unique_note_count
    CHUNK = 1024
    FORMAT = pyaudio.paInt16 # .wav format dtype
    PREC_LIMIT = 1e-8


    # Set default values (will be changed if not using defaults)
    channels = default_input_device.get('maxInputChannels')
    rate = int(default_input_device.get('defaultSampleRate'))

    # We need to be able to identify the index of our desired input device
    numdev = p.get_host_api_info_by_index(0).get('deviceCount')
    for i in range(numdev):
        current_device = p.get_device_info_by_host_api_device_index(0, i)

        # If desired input device is found, use it
        if current_device.get("name") == desired_input_device:
            print("Device \"" + desired_input_device + "\" found.  Will use this device for inputting audio.")
            rate = int(current_device.get('defaultSampleRate'))
            channels = current_device.get('maxInputChannels')
            desired_input_device_idx = i
            found_device = True

    # If desired input device is not found, inform user default input device has been selected
    if not found_device:
        print(desired_input_device + " not found.  Defaulting to " + default_input_device.get('name') + " for audio input.")

    if found_device:
        stream = p.open(format=FORMAT,channels=2,
                        rate=rate,
                        input_device_index=desired_input_device_idx,
                        input=True,
                        stream_callback=callback)
    else:
        stream = p.open(format=FORMAT,
                        channels=channels,
                        rate=rate,
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

        

        unique_note_count = dict() # Reset dictionary

    stream.stop_stream()
    stream.close()
    p.terminate()

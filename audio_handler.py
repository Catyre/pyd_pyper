import numpy as np
import time
import aubio
import sounddevice as sd


# Initialize pitch detection
buffsize = 2048
hopsize = 1024
pitch_o_L = aubio.pitch("default", buffsize, hopsize, 44100)
pitch_o_R = aubio.pitch("default", buffsize, hopsize, 44100)
pitch_o_L.set_unit("Hz")
pitch_o_R.set_unit("Hz")
pitch_o_L.set_silence(-40)  # Silence threshold in dB
pitch_o_R.set_silence(-40)
channels = 2 #Hard coded stereo output

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


# Callback function to process audio in real time
def callback(indata, frames, time, status):
    if status:
        print(status)
    samples = np.frombuffer(indata, dtype=np.float32)

    # Reshape interleaved stereo data into separate channels
    samples = samples.reshape(-1, channels)  # Shape: (frames, 2)
    samples /= np.max(np.abs(samples)) + 1e-10  # Normalize to [-1, 1]

    left_channel = samples[:, 0]
    right_channel = samples[:,1]

    #print(samples)
    pitch_L = pitch_o_L(left_channel[:hopsize])[0]
    pitch_R = pitch_o_R(right_channel[:hopsize])[0]
    #note = aubio.freq2note(pitch)
    #if pitch:
    print(f"Detected Pitch: ({pitch_L:.2f}, {pitch_R:.2f}) Hz")
        #print(f"Detected note: {note}")


class AudioHandler(object):
    def __init__(self):
        self.unique_note_count = {}
        self.devices = sd.query_devices()
        self.tuning = 0
        self.initial_tune_check = False
        self.running = False # On/off switch
        self.CHUNK = 1024
        self.HOPSIZE = 512


    def start(self, device=None):
        self.running = True

        # Get maximum input channels and default sample rate
        self.CHANNELS = device['max_input_channels']
        self.RATE = int(device['default_samplerate'])
        print(device['name'], self.CHANNELS, self.RATE)
       # Open audio stream
        with sd.InputStream(device=device['index'], callback=callback, channels=2, samplerate=44100, blocksize=hopsize):
            print("Listening... Press Ctrl+C to stop.")
            while self.running:
                pass  # Keep the stream running
 


    def stop(self):
        self.running = False


    def get_devices(self):
        return self.devices


    def is_active(self):
        return self.running


    def use_instrument(self, instr):
        self.instr = instr

   
    def calibrate(self, audio):
        print("Calibration: Please play a single note and sustain it until calibration is complete.")
        time.sleep(2)
        self.tuning = librosa.pitch_tuning(y=audio, sr=self.RATE)
        print(f"Adjusting pitch by {self.tuning*100}% of a note\nCalibration complete.  Recording now...")
    

    # Cleaning the audio seems to fuck up the analysis; investigate further
    def callback_old(self, in_data, frame_count, time_info, flag):
        audio = byte_to_float(in_data) # Convert audio byte data to float data

        if not self.initial_tune_check:
            self.calibrate(audio)
            self.initial_tune_check = True

        audio_corrected = librosa.effects.pitch_shift(y=audio, n_steps=self.tuning, sr=self.RATE)
        pitches, _, _ = librosa.pyin(y=audio, n_thresholds=50, fill_na=0.0, frame_length=self.CHUNK, sr=self.RATE, fmin=librosa.note_to_hz(self.instr.note_range[0]), fmax=librosa.note_to_hz(self.instr.note_range[1]))
        pitches = [pitch for pitch in pitches if pitch != 0.]
        geo_mean = np.exp(np.mean(np.log(pitches)))

        if not np.isnan(geo_mean):
            #print(f"Pitches: {pitches}\nGeometric mean: {geo_mean}")
            note = librosa.hz_to_note(geo_mean)

            if self.unique_note_count.get(note) is None:
                self.unique_note_count[note] = 1
            else:
                self.unique_note_count[note] += 1

        return None, pyaudio.paContinue


    def reset_unique_note_count(self):
        self.unique_note_count = {}


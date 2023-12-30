import numpy as np
import pyaudio
import time
import librosa


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


class AudioHandler(object):
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.unique_note_count = {}
        self.devices = [self.p.get_device_info_by_host_api_device_index(0, i) for i in range(self.p.get_host_api_info_by_index(0).get('deviceCount'))]
        self.tuning = 0
        self.initial_tune_check = False


    def start(self, device=None, format=pyaudio.paInt16, chunk=1024):
        self.CHANNELS = device.get('maxInputChannels')
        self.RATE = int(device.get('defaultSampleRate'))
        self.CHUNK = chunk
        self.FORMAT = format

        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  output=False,
                                  stream_callback=self.callback,
                                  frames_per_buffer=self.CHUNK,
                                  input_device_index=device.get('index'))

    def stop(self):
        self.stream.close()
        self.p.terminate()


    def get_devices(self):
        return self.devices


    def is_active(self):
        return self.stream.is_active()


    def use_instrument(self, instr):
        self.instr = instr

   
    def calibrate(self, audio):
        print("Calibration: Please play a single note and sustain it until calibration is complete.")
        time.sleep(2)
        self.tuning = librosa.estimate_tuning(y=audio, sr=self.RATE)
        print(f"Adjusting pitch by {self.tuning*100}% of a note\nCalibration complete.  Recording now...")
    

    # Cleaning the audio seems to fuck up the analysis; investigate further
    def callback(self, in_data, frame_count, time_info, flag):
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


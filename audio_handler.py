import numpy as np
import time
import aubio
import sounddevice as sd
from scipy.signal import butter, filtfilt


# Initialize pitch detection
buffsize = 4096
hopsize = 2048
tolerance = 0.8
latest_pitch = None
note_history = []

# Initialize pitch detection for left and right channels (only use left in case of mono)
#   TODO: Fix hardcoded sample rate
pitch_o_L = aubio.pitch("default", buffsize, hopsize, 44100)
pitch_o_L.set_unit("Hz")
pitch_o_L.set_tolerance(tolerance)
pitch_o_L.set_silence(-40)  # Silence threshold in dB

pitch_o_R = aubio.pitch("default", buffsize, hopsize, 44100)
pitch_o_R.set_unit("Hz")
pitch_o_R.set_silence(-40)
pitch_o_R.set_tolerance(tolerance)


def callback_stereo(indata, frames, time, status):
    global latest_pitch

    if status:
        print(status)
    
    indata /= np.max(np.abs(indata)) + 1e-10 # Normalize input
    samples_L = np.array(indata[:, 0], dtype=np.float32).copy()  # Extract first channel & ensure writeable
    samples_R = np.array(indata[:, 1], dtype=np.float32).copy()  # Do same for second

    # Ensure correct input size for aubio
    if len(samples_L) >= hopsize and len(samples_R) >= hopsize:
        # If so, run sample through pitch detection
        pitch_L = pitch_o_L(samples_L[:hopsize])[0]
        pitch_R = pitch_o_R(samples_R[:hopsize])[0]

        # Ignore unrealistic frequencies
        if 20 < pitch_L < 1000 or 20 < pitch_R < 1000:
            print(f"Detected Frequency (L, R): ({pitch_L:.2f}, {pitch_R:.2f}) Hz")
            print(f"Note value: {aubio.freq2note(pitch_R)}")
            # ^^^ For Debugging ^^^

            latest_pitch = [pitch_L, pitch_R]


def callback_mono(indata, frames, time, status):
    global latest_pitch
    if status:
        print(status)
    
    indata /= np.max(np.abs(indata)) + 1e-10 # Normalize input
    samples = np.array(indata[:, 0], dtype=np.float32).copy()  # Extract first channel & ensure writeable

    # Ensure correct input size for aubio
    if len(filtered_samples_L) >= hopsize and len(filtered_samples_R) >= hopsize:
        pitch = pitch_o_L(samples[:hopsize])[0]

        # Ignore unrealistic frequencies
        if 20 < pitch < 1000:
            print(f"Detected Frequency: {pitch_L:.2f} Hz") # For debugging
            latest_pitch = pitch


class AudioHandler(object):
    def __init__(self):
        self.devices = sd.query_devices()
        self.running = False # On/off switch
        self.CHUNK = 1024
        self.HOPSIZE = 512
        self.note = None
        self.note_duration = None
        self.note_onset = None


    def start(self, device=None):
        global latest_pitch
        self.running = True

        # Get maximum input channels and default sample rate
        self.CHANNELS = device['max_input_channels']
        self.RATE = int(device['default_samplerate'])
    
        if self.CHANNELS == 1:
            # Open audio stream
            with sd.InputStream(device=device['index'], callback=callback_mono, channels=1, samplerate=self.RATE, blocksize=hopsize):
                print("Listening... Press Ctrl+C to stop.")
                while self.running:
                    # Outputting keypresses needs to happen here (put the code in rat.py though)
                    if self.note != latest_pitch
                        self.note_onset = time.time()
                        self.note = latest_pitch
                        note_history.append(self.note, self.note_onset)

        elif self.CHANNELS == 2:
            with sd.InputStream(device=device['index'], callback=callback_stereo, channels=2, samplerate=self.RATE, blocksize=hopsize):
                print("Listening... Press Ctrl+C to stop.")
                while self.running:
                    # Outputting keypresses needs to happen here (put the code in rat.py though)
                    if self.note != latest_pitch
                        self.note_onset = time.time()
                        self.note = latest_pitch
                        note_history.append(self.note, self.note_onset)
 


    def stop(self):
        self.running = False


    def get_devices(self):
        return self.devices


    def is_active(self):
        return self.running

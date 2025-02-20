import numpy as np
import time
import aubio
import rat  # Plague be upon us...
import collections
import sounddevice as sd
from scipy.signal import butter, filtfilt


# Initialize pitch detection
MIN_NOTE_DURATION = 0.15  # seconds 
PITCH_DEVIATION_TOLERANCE = 3  # Hz
HARMONIC_THRESHOLD = 1.5
stable_pitch_window = collections.deque(maxlen=5)

buffsize = 4096
hopsize = 2048
tolerance = 0.8
latest_pitch = None
note_start_time = 0.0
note_history = []
note_durations = []

# Initialize pitch detection for left and right channels (only use left in case of mono)
#   TODO: Fix hardcoded sample rate
pitch_o_L = aubio.pitch("default", buffsize, hopsize, 44100)
pitch_o_L.set_unit("Hz")
pitch_o_L.set_tolerance(tolerance)
pitch_o_L.set_silence(-10)  # Silence threshold in dB

pitch_o_R = aubio.pitch("default", buffsize, hopsize, 44100)
pitch_o_R.set_unit("Hz")
pitch_o_R.set_silence(-10)
pitch_o_R.set_tolerance(tolerance)


def is_pitch_stable(new_pitch):
    """ Check if new pitch is stable compared to recent history. """
    if len(stable_pitch_window) < stable_pitch_window.maxlen:
        return False  # Not enough data yet

    avg_pitch = np.mean(stable_pitch_window)
    return abs(new_pitch - avg_pitch) < PITCH_DEVIATION_TOLERANCE


def is_harmonic(new_pitch, reference_pitch):
    """ Ignore harmonics that are multiples of the fundamental frequency. """
    if reference_pitch is None:
        return False  # No previous reference
    ratio = new_pitch / reference_pitch
    return (1.8 > ratio > HARMONIC_THRESHOLD) or (3.2 > ratio > 2.8)  # Check if 1.5x, 2x, 3x, etc.


def callback(indata, frames, time_info, status):
    global latest_pitch, note_start_time

    if status:
        print(status)

    indata /= np.max(np.abs(indata)) + 1e-10 # Normalize input

    # Detect number of channels dynamically, flatten stereo into an averaged mono
    if indata.shape[1] == 2:  # Stereo input
        samples = np.array(indata[:, 1], dtype=np.float32).copy()  # Extract first channel & ensure writeable
    else:  # Mono input
        samples = np.array(indata, dtype=np.float32).copy()  # Convert to mono by averaging

    # Detect pitch
    pitch = pitch_o_L(samples[:hopsize])[0]
    #print(pitch)

    # Filter invalid values
    if 20 < pitch < 500:
        pitch = round(pitch, 2)
    else:
        pitch = None

    # Ignore small fluctuations
    if pitch:
        stable_pitch_window.append(pitch)
        if not is_pitch_stable(pitch):
            return

    # Ignore harmonics
    if pitch and is_harmonic(pitch, latest_pitch):
        return

    # Detect note start
    if pitch and latest_pitch is None:
        latest_pitch = pitch
        note_start_time = time.time()
        print(f"Note {aubio.freq2note(pitch)} started")

    # Detect note continuation
    elif pitch and latest_pitch == pitch:
        pass

    # Detect note end
    elif latest_pitch and (pitch is None or abs(pitch - latest_pitch) > PITCH_DEVIATION_TOLERANCE):
        note_duration = time.time() - note_start_time

        if note_duration >= MIN_NOTE_DURATION:
            note_durations.append((latest_pitch, note_duration))
            print(f"Note {aubio.freq2note(latest_pitch)} ended, Duration: {note_duration:.2f}s")

        # Reset tracking
        latest_pitch = None
        note_start_time = None


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
    
        # Question for Hudson: how to escape this callback loop for a moment to give the appropriate keypress *without* actually exiting the loop
        if self.CHANNELS == 1:
            # Open audio stream
            with sd.InputStream(device=device['index'], callback=callback_mono, channels=1, samplerate=self.RATE, blocksize=hopsize):
                print("Listening... Press Ctrl+C to stop.")
                latest_note_R = aubio.freq2note(latest_pitch[0]) # May break mono

                while self.running:
                    # Outputting keypresses needs to happen here (put the code in rat.py though)
                    if self.note != latest_note_R:
                        self.note_onset = time.time()
                        self.note = latest_note_R
                        print(f"Detected note: {aubio.freq2note(self.note[1])}")
                        note_history.append([self.note, self.note_onset])

        elif self.CHANNELS == 2:
            with sd.InputStream(device=device['index'], callback=callback, channels=2, samplerate=self.RATE, blocksize=hopsize):
                print("Listening... Press Ctrl+C to stop.")

                while self.running:
                    pass 


    def stop(self):
        self.running = False


    def get_devices(self):
        return self.devices


    def is_active(self):
        return self.running

    def use_instrument(self, instr):
        self.instr = instr

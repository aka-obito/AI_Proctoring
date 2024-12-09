import pyaudio
import numpy as np

# Placeholders and global variables
SOUND_AMPLITUDE = 0
AUDIO_CHEAT = 0

# Sound variables
CALLBACKS_PER_SECOND = 38               # Callbacks per second (system dependent)
SUS_FINDING_FREQUENCY = 2               # Calculates SUS *n* times every second
SOUND_AMPLITUDE_THRESHOLD = 20          # Amplitude considered for SUS calc

# Packing *n* frames to calculate SUS
FRAMES_COUNT = int(CALLBACKS_PER_SECOND / SUS_FINDING_FREQUENCY)
AMPLITUDE_LIST = [0] * FRAMES_COUNT
SUS_COUNT = 0
count = 0

# PyAudio constants
CHUNK = 1024                            # Number of audio frames per buffer
FORMAT = pyaudio.paInt16                # Format for audio input
CHANNELS = 1                            # Number of audio channels
RATE = 44100                            # Sampling rate

def calculate_rms(audio_data):
    """Calculate the Root Mean Square (RMS) value of the audio data."""
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    return np.sqrt(np.mean(audio_array**2)) * 1000  # Scaling factor for better readability

def callback(in_data, frame_count, time_info, status):
    global SOUND_AMPLITUDE, SUS_COUNT, count, SOUND_AMPLITUDE_THRESHOLD, AUDIO_CHEAT
    rms_amplitude = calculate_rms(in_data)
    AMPLITUDE_LIST.append(rms_amplitude)
    count += 1
    AMPLITUDE_LIST.pop(0)

    if count == FRAMES_COUNT:
        avg_amp = sum(AMPLITUDE_LIST) / FRAMES_COUNT
        SOUND_AMPLITUDE = avg_amp

        if SUS_COUNT >= 2:
            AUDIO_CHEAT = 1
            SUS_COUNT = 0

        if avg_amp > SOUND_AMPLITUDE_THRESHOLD:
            SUS_COUNT += 1
        else:
            SUS_COUNT = 0
            AUDIO_CHEAT = 0

        count = 0

    return (None, pyaudio.paContinue)

def sound():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

    try:
        stream.start_stream()
        while stream.is_active():
            pass
    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()
        p.terminate()

def sound_analysis():
    global AMPLITUDE_LIST, FRAMES_COUNT, SOUND_AMPLITUDE
    while True:
        AMPLITUDE_LIST.append(SOUND_AMPLITUDE)
        AMPLITUDE_LIST.pop(0)

        avg_amp = sum(AMPLITUDE_LIST) / FRAMES_COUNT

        if avg_amp > 10:
            print("Sus...")

if __name__ == "__main__":
    sound()

import sounddevice as sd 
import wave
import numpy as np

# Placeholders and global variables
SOUND_AMPLITUDE = 0
AUDIO_CHEAT = 0

# Sound monitoring variables
CALLBACKS_PER_SECOND = 38               # Callbacks per second (system dependent)
SUS_FINDING_FREQUENCY = 2               # Calculates SUS *n* times every second
SOUND_AMPLITUDE_THRESHOLD = 20          # Amplitude considered for SUS calc 

# Packing *n* frames to calculate SUS
FRAMES_COUNT = int(CALLBACKS_PER_SECOND / SUS_FINDING_FREQUENCY)
AMPLITUDE_LIST = [0] * FRAMES_COUNT
SUS_COUNT = 0
count = 0

# Recording settings
SAMPLE_RATE = 44100  # 44.1 kHz sample rate
CHANNELS = 1         # Mono audio


def calculate_rms(indata):
    """Calculate the Root Mean Square (RMS) value of the audio data."""
    return np.sqrt(np.mean(indata**2)) * 1000  # Scaling factor for better readability


def print_sound(indata, outdata, frames, time, status):
    """Callback function for real-time sound monitoring."""
    global SOUND_AMPLITUDE, SUS_COUNT, count, SOUND_AMPLITUDE_THRESHOLD, AUDIO_CHEAT
    rms_amplitude = calculate_rms(indata)
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


def sound():
    """Monitor real-time sound amplitude."""
    with sd.Stream(callback=print_sound):
        sd.sleep(-1)


def record_audio():
    """Record audio and save it as a .wav file."""
    print("Recording started... Press Ctrl+C to stop.")
    recording = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        recording.extend(indata[:, 0] * 32767)  # Convert to 16-bit PCM

    try:
        with sd.InputStream(callback=callback, samplerate=SAMPLE_RATE, channels=CHANNELS):
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        print("\nRecording stopped.")
        save_audio(recording)


def save_audio(data):
    """Save the recorded audio to a .wav file."""
    filename = "recorded_audio.wav"
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(np.array(data, dtype=np.int16).tobytes())
    print(f"Audio saved as '{filename}'.")


if __name__ == "__main__":
    # Run sound monitoring and recording as standalone for testing
    choice = input("Enter '1' to monitor audio or '2' to record audio: ")
    if choice == '1':
        sound()
    elif choice == '2':
        record_audio()
    else:
        print("Invalid choice.")

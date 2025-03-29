import librosa
import hashlib
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
from scipy.signal import correlate2d
from flask import Flask, request, render_template
import os

# Load song and record the fingerprint
def generate_fingerprint(audio_file):
    y, sr = librosa.load(audio_file, sr=22050, mono=True)
    y = librosa.util.normalize(y)

    S = librosa.feature.melspectrogram(y=y, sr=sr)
    S_db = librosa.amplitude_to_db(S, ref=np.max)
    return S_db  # Return spectrogram

# Cross-correlation matching function
def match_spectrograms(stored_spectrogram, recorded_spectrogram, threshold=0.8):
    corr = correlate2d(stored_spectrogram, recorded_spectrogram, mode='same', boundary='wrap')
    # Find the maximum correlation value
    max_corr = np.max(corr)
    print(f"Maximum correlation: {max_corr}")

    if max_corr >= threshold:
        return True
    else:
        return False

# Function to record audio
def record_audio(duration=5, sample_rate=22050):
    print("Recording... Play the song!")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()
    print("Recording complete!")

    wav.write("recorded_audio.wav", sample_rate, audio)
    return "recorded_audio.wav"

# Store and compare functions
def store_fingerprint(song_name, audio_file):
    fingerprint = generate_fingerprint(audio_file)
    fingerprint_db[song_name] = fingerprint
    print(f"Stored fingerprint for {song_name}")

def match_song(recorded_spectrogram):
    # Iterate through the stored fingerprints and check for a match
    for song_name, stored_spectrogram in fingerprint_db.items():
        if match_spectrograms(stored_spectrogram, recorded_spectrogram):
            return song_name  # Return the song name if a match is found
    return None  # Return None if no match is found


# Dictionary to store fingerprints
fingerprint_db = {}

# Example: Store the fingerprint for "Blinding Lights"
store_fingerprint("Blinding Lights", "weeknd.mp3")
"""
# Record the audio and generate its fingerprint
recorded_file = record_audio()
recorded_spectrogram = generate_fingerprint(recorded_file)

# Now, compare the recorded spectrogram with stored spectrograms
for song_name, stored_spectrogram in fingerprint_db.items():
    if match_spectrograms(stored_spectrogram, recorded_spectrogram):
        print(f"Match found! The song is: {song_name}")
        break
else:
    print("No match found.")


"""


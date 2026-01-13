import sounddevice as sd
import soundfile as sf

print("=" * 50)
print("SPEAK CLEARLY AND LOUDLY")
print("Say: 'This is a test of the meeting notes application'")
print("=" * 50)
print("\n🎤 Recording in 3 seconds...")

import time
time.sleep(3)

print("🔴 RECORDING NOW - SPEAK!")

duration = 10  # 10 seconds
sample_rate = 16000

recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
sd.wait()

sf.write("clear_test.wav", recording, sample_rate)
print("✅ Saved as clear_test.wav")

# Play it back
print("\n🔊 Playing back...")
sd.play(recording, sample_rate)
sd.wait()
import sounddevice as sd
import soundfile as sf

print("🎤 Recording 5 seconds of audio...")
duration = 5
sample_rate = 16000

# Record
recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
sd.wait()

# Save
filename = "test_recording.wav"
sf.write(filename, recording, sample_rate)

print(f"✅ Saved as {filename}")
print(f"📁 Location: C:\\Users\\Jadhav\\meeting-notes-app\\{filename}")

# Try to play it back
print("\n🔊 Playing back...")
sd.play(recording, sample_rate)
sd.wait()
print("✅ Playback done!")
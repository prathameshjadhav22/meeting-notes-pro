import whisper
import soundfile as sf
import numpy as np

print("📥 Loading Whisper model...")
model = whisper.load_model("base")

print("🎯 Loading audio file...")
audio_data, sample_rate = sf.read("clear_test.wav")  # Use new file
audio_data = audio_data.astype(np.float32).flatten()

if sample_rate != 16000:
    print(f"⚠️ Resampling from {sample_rate} to 16000 Hz...")
    from scipy import signal
    audio_data = signal.resample(audio_data, int(len(audio_data) * 16000 / sample_rate))

print("🤖 Transcribing (English)...")
result = model.transcribe(audio_data, fp16=False, language="english")  # Force English!

print("\n📝 TRANSCRIPT:")
print("=" * 50)
print(result["text"])
print("=" * 50)
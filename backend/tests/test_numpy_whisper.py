import whisper
import soundfile as sf
import numpy as np
import librosa

y, sr = sf.read(r'C:\Users\Lenovo\Downloads\ai_fraud_call_spoken_demo.wav')
if len(y.shape) > 1:
    y = np.mean(y, axis=1)
if sr != 16000:
    y = librosa.resample(y, orig_sr=sr, target_sr=16000)

y = y.astype(np.float32)
print(f"Loaded audio array: shape={y.shape}, sr=16000, duration={len(y)/16000:.2f}s")

model = whisper.load_model('base')
res = model.transcribe(y, fp16=False, language='en')
print("\n=== TRANSCRIPTION SUCCESS ===")
print("FULL TEXT:\n", res['text'])
print(f"\nSEGMENTS ({len(res['segments'])}):")
for s in res['segments']:
    print(f"[{s['start']:.1f}s - {s['end']:.1f}s]: {s['text']}")

import whisper

model = whisper.load_model('base')
res = model.transcribe(r'C:\Users\Lenovo\Downloads\ai_fraud_call_spoken_demo.wav', fp16=False)
print('TRANSCRIPT:\n', res['text'])
print('\nSEGMENTS COUNT:', len(res['segments']))
for s in res['segments']:
    print(f"[{s['start']:.1f}s - {s['end']:.1f}s]: {s['text']}")

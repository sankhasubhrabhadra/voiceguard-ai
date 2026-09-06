import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\Lenovo\.gemini\antigravity\scratch\voiceguard-ai\backend')

from app.audio_processor import AudioProcessor
from app.classifier import VoiceCloneClassifier

proc = AudioProcessor()
clf = VoiceCloneClassifier()

for name in ['ai_fraud_call_spoken_demo.wav', 'lawyer_benign_test.wav']:
    path = os.path.join(r'C:\Users\Lenovo\Downloads', name)
    print('='*70)
    print(f'FILE: {name}')
    y, sr = proc.load_audio(path)
    feats, feat_vec, raw = proc.extract_features(y, sr)
    spec_data, anoms = proc.generate_spectrogram_and_waveform(y, sr)
    
    scaled_vec = clf.scaler.transform(feat_vec.reshape(1, -1))
    probs = clf.model.predict_proba(scaled_vec)[0]
    print(f'RF predict_proba: Human={probs[0]:.4f}, Clone={probs[1]:.4f}')
    
    res = clf.predict(feats, feat_vec, raw, anoms)
    print(f'Voice Risk Score: {res.risk_score}%')
    print(f'Is Cloned: {res.is_cloned}, Confidence: {res.confidence}%')
    print(f'Vocoder Biomarkers ({len(res.vocoder_biomarkers)}): {[b["name"] for b in res.vocoder_biomarkers]}')
    print(f'Anomaly Summary: total={res.anomaly_summary.total_anomalies}, score={res.anomaly_summary.anomaly_score}')

import sys
import os
import hashlib

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\Lenovo\.gemini\antigravity\scratch\voiceguard-ai\backend')

from app.audio_processor import AudioProcessor
from app.classifier import VoiceCloneClassifier
from app.stt_engine import STTEngine
from app.scam_detector import ScamDetector
from app.fusion import RiskFusionEngine

proc = AudioProcessor()
clf = VoiceCloneClassifier()
stt = STTEngine()
scam = ScamDetector()

f1 = r'C:\Users\Lenovo\Downloads\ai_fraud_call_spoken_demo.wav'
f2 = r'C:\Users\Lenovo\Downloads\lawyer_benign_test.wav'

for f in [f1, f2]:
    print('='*70)
    print(f'ANALYZING: {f}')
    with open(f, 'rb') as audio_bytes:
        h = hashlib.sha256(audio_bytes.read()).hexdigest()[:12]
    print(f'File Hash: {h}')
    
    y, sr = proc.load_audio(f)
    print(f'Samples: {len(y)}, SR: {sr}, Duration: {len(y)/sr:.2f}s')
    feats, feat_vec, raw = proc.extract_features(y, sr)
    spec_data, anoms = proc.generate_spectrogram_and_waveform(y, sr)
    
    bio_score, detected_bios = clf.evaluate_vocoder_biomarkers(feats, raw)
    print(f'Biomarker score: {bio_score}')
    print(f'Detected biomarkers count: {len(detected_bios)}')
    for b in detected_bios:
        print(f"   * {b['name']}: measured={b['value']}, normal={b['normal']}")
    
    scaled_vec = clf.scaler.transform(feat_vec.reshape(1, -1))
    probs = clf.model.predict_proba(scaled_vec)[0]
    print(f'RF predict_proba (0=Human, 1=Clone): {probs}')
    
    res = clf.predict(feats, feat_vec, raw, anoms)
    print(f'Voice risk score: {res.risk_score}%, is_cloned: {res.is_cloned}')
    print(f'Pitch std: {feats.pitch_std:.2f} Hz, jitter: {feats.pitch_jitter_local:.3f}%, shimmer: {feats.amplitude_shimmer_local:.3f}%')
    print(f'Pitch accel var: {feats.pitch_acceleration_variance:.4f}, silence floor: {feats.silence_noise_floor_db:.2f} dB')
    print(f'Flux mean: {feats.spectral_flux_mean:.4f}, Flatness: {feats.spectral_flatness_mean:.6f}')
    print(f'Anomalies count: {len(anoms)}')

    stt_res = stt.transcribe(f, y=y, sr=sr)
    print(f"Transcript: \"{stt_res['full_text']}\"")
    scam_res = scam.analyze_transcript(stt_res['full_text'], stt_res['segments'])
    print(f"Scam script risk score: {scam_res.script_risk_score}%, matches: {len(scam_res.matches)}")
    print(f"Social engineering: {scam_res.social_engineering.model_dump() if scam_res.social_engineering else None}")

    fusion = RiskFusionEngine.fuse(res, scam_res)
    print(f"Overall Risk: {fusion.overall_risk_score}%, Level: {fusion.risk_level}")
    print(f"Risk Reasons:")
    for r in fusion.risk_reasons:
        print(f"   - {r}")

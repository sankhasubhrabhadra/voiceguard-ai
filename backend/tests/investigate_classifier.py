import os
import sys
import joblib
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\Lenovo\.gemini\antigravity\scratch\voiceguard-ai\backend')

from app.audio_processor import AudioProcessor
from app.classifier import VoiceCloneClassifier

proc = AudioProcessor()
clf = VoiceCloneClassifier()

model_path = r'C:\Users\Lenovo\.gemini\antigravity\scratch\voiceguard-ai\backend\app\rf_voice_model_v3.joblib'
print('=' * 80)
print('INVESTIGATION: MODEL & CODE PATH INSPECTION')
print('=' * 80)
print(f'Model File Exists: {os.path.exists(model_path)}')
if os.path.exists(model_path):
    saved = joblib.load(model_path)
    print(f"Saved Keys: {list(saved.keys())}")
    print(f"Classifier Class: {type(saved['model']).__name__}")
    print(f"Number of Trees (n_estimators): {len(saved['model'].estimators_)}")
    print(f"Max Depth: {saved['model'].max_depth}")
    print(f"Scaler Feature Count: {saved['scaler'].n_features_in_}")

test_files = [
    ('Genuine 1 (Legitimate Support Call)', r'C:\Users\Lenovo\.gemini\antigravity\scratch\voiceguard-ai\backend\sample_audios\sample_4_legitimate_call.wav'),
    ('Genuine 2 (Human Bank Caller)', r'C:\Users\Lenovo\.gemini\antigravity\scratch\voiceguard-ai\backend\sample_audios\sample_2_otp_theft_human.wav'),
    ('Genuine 3 (Lawyer Benign Test)', r'C:\Users\Lenovo\Downloads\lawyer_benign_test.wav'),
    ('Synthetic 1 (Digital Arrest AI Clone)', r'C:\Users\Lenovo\.gemini\antigravity\scratch\voiceguard-ai\backend\sample_audios\sample_1_digital_arrest_clone.wav'),
    ('Synthetic 2 (AI Assistant Meeting Clone)', r'C:\Users\Lenovo\.gemini\antigravity\scratch\voiceguard-ai\backend\sample_audios\sample_3_ai_clone_benign.wav'),
    ('Synthetic 3 (Fraud Spoken Demo Speech)', r'C:\Users\Lenovo\Downloads\ai_fraud_call_spoken_demo.wav'),
]

print('\n' + '=' * 105)
print(f"{'Sample Label':<35} | {'Raw RF Clone %':<16} | {'Biomarker %':<13} | {'Final Risk %':<13} | {'Verdict'}")
print('-' * 105)

for label, fpath in test_files:
    if not os.path.exists(fpath):
        print(f"{label}: NOT FOUND ({fpath})")
        continue
    y, sr = proc.load_audio(fpath)
    feats, feat_vec, raw = proc.extract_features(y, sr)
    spec_data, anoms = proc.generate_spectrogram_and_waveform(y, sr)
    
    scaled_vec = clf.scaler.transform(feat_vec.reshape(1, -1))
    probs = clf.model.predict_proba(scaled_vec)[0]
    rf_clone_prob = float(probs[1]) * 100.0
    
    bio_score, detected_bios = clf.evaluate_vocoder_biomarkers(feats, raw)
    res = clf.predict(feats, feat_vec, raw, anoms)
    
    verdict = 'SYNTHETIC CLONE' if res.is_cloned else 'AUTHENTIC HUMAN'
    print(f"{label:<35} | {rf_clone_prob:<15.2f}% | {bio_score:<12.2f}% | {res.risk_score:<12.1f}% | {verdict}")

print('=' * 105)

# Detailed raw feature breakdown for lawyer_benign_test.wav & ai_fraud_call_spoken_demo.wav
for name, fpath in [('lawyer_benign_test.wav', r'C:\Users\Lenovo\Downloads\lawyer_benign_test.wav'), ('ai_fraud_call_spoken_demo.wav', r'C:\Users\Lenovo\Downloads\ai_fraud_call_spoken_demo.wav')]:
    print(f"\n--- RAW FEATURE VECTOR BREAKDOWN: {name} ---")
    y, sr = proc.load_audio(fpath)
    feats, feat_vec, raw = proc.extract_features(y, sr)
    print(f"Total Feature Dimensions: {len(feat_vec)}")
    print(f"Duration: {feats.duration_seconds}s, Sample Rate: {feats.sample_rate}, Samples: {len(y)}")
    print(f"Mean Pitch F0: {feats.mean_pitch_hz} Hz, Pitch Std: {feats.pitch_std} Hz")
    print(f"Pitch Jitter: {feats.pitch_jitter_local:.4f}%, Shimmer: {feats.amplitude_shimmer_local:.4f}%")
    print(f"Pitch Accel Var: {feats.pitch_acceleration_variance:.4f}, Pitch Vel Std: {raw.get('pitch_vel_std', 0):.4f}")
    print(f"Silence Floor: {feats.silence_noise_floor_db} dB, HNR: {feats.harmonic_to_noise_ratio_db} dB")
    print(f"Voiced Spectral Flatness: {feats.spectral_flatness_mean:.6f}, Spectral Flux: {feats.spectral_flux_mean:.4f}")
    print(f"Spectral Centroid: {feats.spectral_centroid_mean} Hz, Rolloff: {feats.spectral_rolloff_mean} Hz")
    print(f"MFCC 1-5 Means: {feats.mfcc_means[:5]}")
    print(f"MFCC 16-20 Means: {feats.mfcc_means[15:]}")
    print(f"Spectral Contrast (7 bands): {feats.spectral_contrast_mean}")

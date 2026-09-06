import sys
import os
import hashlib
import numpy as np
import librosa
import soundfile as sf

sys.stdout.reconfigure(encoding='utf-8')

f1 = r'C:\Users\Lenovo\Downloads\ai_fraud_call_spoken_demo.wav'
f2 = r'C:\Users\Lenovo\Downloads\lawyer_benign_test.wav'

for f in [f1, f2]:
    print('='*70)
    print(f'INSPECTING: {os.path.basename(f)}')
    with open(f, 'rb') as fp:
        raw_bytes = fp.read()
        file_hash = hashlib.sha256(raw_bytes).hexdigest()[:16]
    print(f'File Size: {len(raw_bytes)} bytes, SHA-256: {file_hash}')
    
    y, sr = sf.read(f)
    if len(y.shape) > 1:
        y = np.mean(y, axis=1)
    if sr != 16000:
        y = librosa.resample(y, orig_sr=sr, target_sr=16000)
        sr = 16000
    
    duration = len(y) / sr
    
    # Pitch extraction via pyin
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7'),
        sr=sr,
        frame_length=2048,
        hop_length=512
    )
    valid_f0 = f0[~np.isnan(f0)] if f0 is not None else np.array([])
    
    # Active voiced frames for spectral features
    D = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
    flatness = librosa.feature.spectral_flatness(S=D)[0]
    centroid = librosa.feature.spectral_centroid(S=D, sr=sr)[0]
    
    # Filter by voiced frames where pitch exists
    if f0 is not None and len(f0) == len(flatness):
        voiced_mask = ~np.isnan(f0)
        voiced_flatness = flatness[voiced_mask] if np.any(voiced_mask) else flatness
        voiced_centroid = centroid[voiced_mask] if np.any(voiced_mask) else centroid
    else:
        voiced_flatness = flatness
        voiced_centroid = centroid

    print(f'Duration: {duration:.2f}s, Samples: {len(y)}')
    print(f'Spectral Flatness: mean={np.mean(flatness):.6f}, voiced_mean={np.mean(voiced_flatness):.6f}')
    print(f'Spectral Centroid: mean={np.mean(centroid):.1f} Hz, voiced_mean={np.mean(voiced_centroid):.1f} Hz')
    print(f'Voiced frames count: {len(valid_f0)}')
    if len(valid_f0) > 3:
        print(f'Pitch F0: Mean = {np.mean(valid_f0):.1f} Hz, Std = {np.std(valid_f0):.1f} Hz, Min = {np.min(valid_f0):.1f} Hz, Max = {np.max(valid_f0):.1f} Hz')
        periods = 1.0 / np.clip(valid_f0, 40.0, 1000.0)
        diff_periods = np.abs(np.diff(periods))
        jitter = np.mean(diff_periods) / (np.mean(periods) + 1e-8) * 100.0
        
        # Pitch acceleration
        pitch_vel = np.diff(valid_f0)
        pitch_accel = np.diff(pitch_vel) if len(pitch_vel) > 1 else np.array([0.0])
        print(f'Pitch Jitter: {jitter:.3f}%, Pitch Accel Variance: {np.var(pitch_accel):.2f}, Pitch Vel Std: {np.std(pitch_vel):.2f}')
    else:
        print('No voiced pitch detected.')

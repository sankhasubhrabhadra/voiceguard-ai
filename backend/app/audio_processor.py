import os
import numpy as np
import librosa
import soundfile as sf
from typing import Dict, Any, Tuple, List, Optional
from app.models import AudioAcousticFeatures, AnomalyRegion

class AudioProcessor:
    def __init__(self, target_sr: int = 16000):
        self.target_sr = target_sr

    def load_audio(self, file_path_or_bytes, sr: Optional[int] = None) -> Tuple[np.ndarray, int]:
        """Loads audio file into floating point numpy array at target sample rate."""
        target_sr = sr or self.target_sr
        try:
            y, sample_rate = librosa.load(file_path_or_bytes, sr=target_sr, mono=True)
        except Exception as e:
            try:
                data, sample_rate = sf.read(file_path_or_bytes)
                if len(data.shape) > 1:
                    data = np.mean(data, axis=1)
                if sample_rate != target_sr:
                    y = librosa.resample(data, orig_sr=sample_rate, target_sr=target_sr)
                    sample_rate = target_sr
                else:
                    y = data
            except Exception as sf_err:
                raise ValueError(f"Failed to decode audio file: {str(e)} | {str(sf_err)}")

        if len(y) == 0:
            raise ValueError("Audio file contains no audio samples.")

        # Normalize audio volume safely
        max_val = np.max(np.abs(y))
        if max_val > 1e-6:
            y = y / max_val

        return y.astype(np.float32), sample_rate

    def extract_features(self, y: np.ndarray, sr: int) -> Tuple[AudioAcousticFeatures, np.ndarray, Dict[str, Any]]:
        """
        Extract comprehensive acoustic & neural vocoder features for deepfake voice forensics.
        Feature representation: 112 dimensions
        (20 mfcc_mean + 20 mfcc_std + 20 mfcc_delta_mean + 20 mfcc_delta_std + 7 contrast_mean + 7 contrast_std + 18 acoustic metrics)
        """
        duration = float(len(y) / sr)
        
        # 1. Pitch & Vocal Tract Perturbation (Jitter, Shimmer, and F0 Dynamics)
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'),
            sr=sr,
            frame_length=2048,
            hop_length=512
        )
        
        valid_f0 = f0[~np.isnan(f0)] if f0 is not None else np.array([])
        voiced_ratio = float(len(valid_f0) / max(1, len(f0))) if f0 is not None else 0.0

        if len(valid_f0) > 3:
            mean_pitch = float(np.mean(valid_f0))
            pitch_std = float(np.std(valid_f0))
            
            # Local Pitch Jitter: relative period-to-period perturbation
            periods = 1.0 / np.clip(valid_f0, 40.0, 1000.0)
            diff_periods = np.abs(np.diff(periods))
            jitter_local = float(np.mean(diff_periods) / (np.mean(periods) + 1e-8) * 100.0)

            # Pitch Velocity and Acceleration (F0 Jerk / Second Derivative)
            pitch_velocity = np.diff(valid_f0)
            pitch_accel = np.diff(pitch_velocity) if len(pitch_velocity) > 1 else np.array([0.0])
            pitch_accel_var = float(np.var(pitch_accel))
            pitch_vel_std = float(np.std(pitch_velocity))
        else:
            mean_pitch = 140.0
            pitch_std = 0.0
            jitter_local = 0.0
            pitch_accel_var = 0.0
            pitch_vel_std = 0.0

        # Amplitude Shimmer: frame-to-frame peak amplitude perturbation on voiced frames
        frame_length = 512
        hop_length = 256
        frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
        amplitudes = np.max(np.abs(frames), axis=0)
        valid_amps = amplitudes[amplitudes > 0.02]
        if len(valid_amps) > 2:
            diff_amps = np.abs(np.diff(valid_amps))
            shimmer_local = float(np.mean(diff_amps) / (np.mean(valid_amps) + 1e-8) * 100.0)
        else:
            shimmer_local = 2.0

        # 2. MFCCs (20 coefficients + delta + delta-delta)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        mfcc_means = np.mean(mfcc, axis=1).tolist()
        mfcc_stds = np.std(mfcc, axis=1).tolist()
        mfcc_delta = librosa.feature.delta(mfcc)
        mfcc_delta_means = np.mean(mfcc_delta, axis=1).tolist()
        mfcc_delta_stds = np.std(mfcc_delta, axis=1).tolist()

        # Higher-order MFCC variance (coeffs 13-20 capture vocoder upsampling artifacts)
        high_mfccs = mfcc[12:20, :]
        high_mfcc_var = float(np.mean(np.var(high_mfccs, axis=1)))

        # 3. Spectral Features (Voiced & Global)
        D = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
        flatness_matrix = librosa.feature.spectral_flatness(S=D)
        flatness_all = flatness_matrix[0]
        
        centroid_matrix = librosa.feature.spectral_centroid(S=D, sr=sr)
        centroid_all = centroid_matrix[0]

        rolloff_matrix = librosa.feature.spectral_rolloff(S=D, sr=sr, roll_percent=0.85)
        rolloff_all = rolloff_matrix[0]

        # Calculate voiced spectral metrics if voiced mask available
        if f0 is not None and len(f0) == len(flatness_all):
            voiced_mask = ~np.isnan(f0)
            v_flatness = flatness_all[voiced_mask] if np.any(voiced_mask) else flatness_all
            v_centroid = centroid_all[voiced_mask] if np.any(voiced_mask) else centroid_all
            v_rolloff = rolloff_all[voiced_mask] if np.any(voiced_mask) else rolloff_all
        else:
            v_flatness = flatness_all
            v_centroid = centroid_all
            v_rolloff = rolloff_all

        flatness_mean = float(np.mean(v_flatness))
        flatness_std = float(np.std(v_flatness))

        centroid_mean = float(np.mean(v_centroid))
        centroid_std = float(np.std(v_centroid))

        rolloff_mean = float(np.mean(v_rolloff))
        rolloff_std = float(np.std(v_rolloff))

        zcr = librosa.feature.zero_crossing_rate(y=y)
        zcr_mean = float(np.mean(zcr))
        zcr_std = float(np.std(zcr))

        # 4. Multi-band Spectral Contrast (octave-based harmonic peaks vs valleys)
        try:
            contrast = librosa.feature.spectral_contrast(y=y, sr=sr, n_bands=6)
            contrast_means = [float(x) for x in np.mean(contrast, axis=1)]
            contrast_stds = [float(x) for x in np.std(contrast, axis=1)]
        except Exception:
            contrast_means = [20.0] * 7
            contrast_stds = [5.0] * 7

        # 5. Spectral Flux / Onset Strength Dynamics
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        spectral_flux_mean = float(np.mean(onset_env))
        spectral_flux_std = float(np.std(onset_env))

        # 6. High-frequency energy cutoff & Harmonic-to-noise ratio
        freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
        hf_mask = freqs >= 7000
        total_energy = np.sum(D**2) + 1e-8
        hf_energy = np.sum(D[hf_mask, :]**2) if np.any(hf_mask) else 0.0
        hf_ratio = float(hf_energy / total_energy)

        # Harmonicity estimation
        harmonic = librosa.effects.harmonic(y)
        noise = y - harmonic
        h_power = np.sum(harmonic**2) + 1e-8
        n_power = np.sum(noise**2) + 1e-8
        hnr_db = float(10.0 * np.log10(h_power / n_power))

        # 7. Silence Noise Floor & Digital Zero Detection
        rms = librosa.feature.rms(y=y, hop_length=512)[0]
        quiet_frames = rms[rms < np.percentile(rms, 25)]
        if len(quiet_frames) > 0:
            min_energy = np.mean(quiet_frames) + 1e-12
            silence_floor_db = float(20.0 * np.log10(min_energy))
        else:
            silence_floor_db = -50.0

        features_obj = AudioAcousticFeatures(
            duration_seconds=round(duration, 2),
            sample_rate=sr,
            mean_pitch_hz=round(mean_pitch, 2),
            pitch_std=round(pitch_std, 2),
            pitch_jitter_local=round(jitter_local, 4),
            amplitude_shimmer_local=round(shimmer_local, 4),
            spectral_flatness_mean=round(flatness_mean, 6),
            spectral_centroid_mean=round(centroid_mean, 2),
            spectral_rolloff_mean=round(rolloff_mean, 2),
            zero_crossing_rate_mean=round(zcr_mean, 4),
            mfcc_means=[round(x, 3) for x in mfcc_means],
            high_frequency_energy_ratio=round(hf_ratio, 4),
            harmonic_to_noise_ratio_db=round(hnr_db, 2),
            spectral_contrast_mean=[round(x, 2) for x in contrast_means],
            spectral_flux_mean=round(spectral_flux_mean, 4),
            pitch_acceleration_variance=round(pitch_accel_var, 4),
            silence_noise_floor_db=round(silence_floor_db, 2),
            vocoder_artifact_score=0.0
        )

        # Assemble exact 112-dimensional feature vector for ML model:
        # 20 + 20 + 20 + 20 + 7 + 7 + 18 = 112 features
        feature_vector = np.concatenate([
            mfcc_means,          # 20
            mfcc_stds,           # 20
            mfcc_delta_means,    # 20
            mfcc_delta_stds,     # 20
            contrast_means,      # 7
            contrast_stds,       # 7
            [
                flatness_mean,       # 1
                flatness_std,        # 2
                centroid_mean,       # 3
                centroid_std,        # 4
                rolloff_mean,        # 5
                rolloff_std,         # 6
                zcr_mean,            # 7
                zcr_std,             # 8
                jitter_local,        # 9
                shimmer_local,       # 10
                hnr_db,              # 11
                spectral_flux_mean,  # 12
                spectral_flux_std,   # 13
                pitch_accel_var,     # 14
                pitch_vel_std,       # 15
                high_mfcc_var,       # 16
                silence_floor_db,    # 17
                hf_ratio             # 18
            ]
        ]).astype(np.float32)

        raw_metrics = {
            "duration": duration,
            "sample_rate": sr,
            "num_samples": len(y),
            "voiced_ratio": voiced_ratio,
            "f0_series": valid_f0.tolist() if len(valid_f0) > 0 else [],
            "flatness_mean": flatness_mean,
            "flatness_std": flatness_std,
            "centroid_mean": centroid_mean,
            "centroid_std": centroid_std,
            "rolloff_mean": rolloff_mean,
            "rolloff_std": rolloff_std,
            "jitter_local": jitter_local,
            "shimmer_local": shimmer_local,
            "hf_ratio": hf_ratio,
            "contrast_means": contrast_means,
            "contrast_stds": contrast_stds,
            "spectral_flux_mean": spectral_flux_mean,
            "spectral_flux_std": spectral_flux_std,
            "pitch_accel_var": pitch_accel_var,
            "pitch_vel_std": pitch_vel_std,
            "high_mfcc_var": high_mfcc_var,
            "silence_floor_db": silence_floor_db,
            "hnr_db": hnr_db
        }

        return features_obj, feature_vector, raw_metrics

    def generate_spectrogram_and_waveform(
        self, y: np.ndarray, sr: int, num_points: int = 150
    ) -> Tuple[Dict[str, Any], List[AnomalyRegion]]:
        """
        Generates downsampled spectrogram & waveform data for frontend rendering
        and flags localized anomalous acoustic intervals (e.g. vocoder artifacts, unnatural harmonics).
        """
        duration = float(len(y) / sr)
        
        # 1. Waveform downsampling (min/max envelopes)
        step = max(1, len(y) // num_points)
        waveform_times = []
        waveform_min = []
        waveform_max = []
        
        for i in range(0, len(y), step):
            chunk = y[i:i + step]
            if len(chunk) > 0:
                t = round((i + len(chunk) / 2) / sr, 3)
                waveform_times.append(t)
                waveform_min.append(round(float(np.min(chunk)), 3))
                waveform_max.append(round(float(np.max(chunk)), 3))

        # 2. Spectrogram (Mel-spectrogram downsampled for web display)
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=32, fmax=sr//2, hop_length=1024)
        S_dB = librosa.power_to_db(S, ref=np.max)
        
        time_bins = S_dB.shape[1]
        step_t = max(1, time_bins // 60)
        
        spectrogram_matrix = []
        time_labels = []
        for t_idx in range(0, time_bins, step_t):
            chunk = S_dB[:, t_idx:min(t_idx + step_t, time_bins)]
            time_labels.append(round((t_idx * 1024) / sr, 2))
            mean_spectrum = np.mean(chunk, axis=1)
            norm_spectrum = np.clip((mean_spectrum + 80.0) / 80.0 * 100.0, 0, 100)
            spectrogram_matrix.append([round(float(v), 1) for v in norm_spectrum])

        # 3. Detect localized anomalous regions (e.g. vocoder buzzing or static envelope)
        anomalies: List[AnomalyRegion] = []
        frame_time = 1024 / sr
        for idx in range(1, len(spectrogram_matrix) - 1):
            t_curr = time_labels[idx]
            spectrum = np.array(spectrogram_matrix[idx])
            hf_energy = np.mean(spectrum[-8:])
            mid_energy = np.mean(spectrum[8:24])
            
            # Anomaly Type 1: High frequency vocoder phase cutoff / buzzing
            if hf_energy > 72.0 and mid_energy < 35.0:
                anomalies.append(AnomalyRegion(
                    start_time=max(0.0, round(t_curr - frame_time * 2, 2)),
                    end_time=min(duration, round(t_curr + frame_time * 2, 2)),
                    anomaly_type="Vocoder High-Frequency Phase Artifact",
                    confidence=88.5,
                    description="Unnatural high-frequency spectral phase distortion typical of synthetic neural vocoders."
                ))
            # Anomaly Type 2: Harmonic rigidity (static harmonic envelope)
            elif np.std(spectrum) < 8.0 and np.mean(spectrum) > 48.0:
                anomalies.append(AnomalyRegion(
                    start_time=max(0.0, round(t_curr - frame_time * 2, 2)),
                    end_time=min(duration, round(t_curr + frame_time * 2, 2)),
                    anomaly_type="Unnatural Formant & Harmonic Rigidity",
                    confidence=86.0,
                    description="Static harmonic envelope lacking natural human vocal micro-tremors."
                ))

        # Consolidate overlapping anomalies
        merged_anomalies: List[AnomalyRegion] = []
        for anom in anomalies:
            if not merged_anomalies:
                merged_anomalies.append(anom)
            else:
                last = merged_anomalies[-1]
                if anom.start_time <= last.end_time + 0.3 and anom.anomaly_type == last.anomaly_type:
                    last.end_time = max(last.end_time, anom.end_time)
                else:
                    merged_anomalies.append(anom)

        spectrogram_data = {
            "waveform": {
                "times": waveform_times,
                "min": waveform_min,
                "max": waveform_max
            },
            "spectrogram": {
                "times": time_labels,
                "frequencies": ["0-500Hz", "500-1kHz", "1-2kHz", "2-4kHz", "4-6kHz", "6-8kHz"],
                "matrix": spectrogram_matrix
            }
        }

        return spectrogram_data, merged_anomalies[:4]

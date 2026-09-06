import os
import wave
import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_audios")
os.makedirs(SAMPLE_DIR, exist_ok=True)

def generate_formant_voice(
    duration: float = 6.0,
    sr: int = 16000,
    base_f0: float = 135.0,
    pitch_jitter: float = 0.008,
    is_synthetic: bool = False
) -> np.ndarray:
    num_samples = int(duration * sr)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    # 1. Pitch trajectory (F0)
    if is_synthetic:
        # Static robotic pitch with minimal pitch variation
        f0_contour = np.full(num_samples, base_f0)
        for i in range(1, int(duration * 2)):
            idx = int(i * sr * 0.5)
            if idx < num_samples:
                f0_contour[idx:] = base_f0 + (i % 2) * 1.5
    else:
        # Natural human pitch glide with physiological laryngeal inertia
        glide = 22.0 * np.sin(2 * np.pi * 0.7 * t) + 10.0 * np.sin(2 * np.pi * 1.8 * t)
        tremor = np.random.normal(0, pitch_jitter * 15.0, num_samples)
        f0_contour = base_f0 + glide + tremor

    # 2. Phase integration for fundamental frequency
    phase = np.cumsum(2 * np.pi * f0_contour / sr)
    
    # 3. Source excitation (glottal pulse train approximation)
    harmonics = np.zeros(num_samples)
    for h in range(1, 16):
        amp = 1.0 / (h ** 1.1)
        harmonics += amp * np.sin(h * phase)

    # 4. Formant Resonators (F1=600Hz, F2=1700Hz, F3=2500Hz)
    def bandpass(data, lowcut, highcut, order=2):
        nyq = 0.5 * sr
        low = max(20.0, lowcut) / nyq
        high = min(nyq - 100.0, highcut) / nyq
        b, a = butter(order, [low, high], btype='band')
        return lfilter(b, a, data)

    formant1 = bandpass(harmonics, 450, 750) * 1.2
    formant2 = bandpass(harmonics, 1400, 2000) * 0.8
    formant3 = bandpass(harmonics, 2200, 2900) * 0.5
    
    voice = formant1 + formant2 + formant3

    # Add vocal tract breath / envelope
    speech_envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 3.2 * t)**2
    pause_mask = np.ones(num_samples)
    for pause_sec in [1.5, 3.2, 4.8]:
        p_start = int(pause_sec * sr)
        p_end = min(num_samples, int((pause_sec + 0.3) * sr))
        pause_mask[p_start:p_end] = 0.05

    voice = voice * speech_envelope * pause_mask

    if is_synthetic:
        # Add high frequency phase buzz and steep cutoff at 6500 Hz (vocoder signature)
        buzz = 0.03 * np.sin(2 * np.pi * 6800.0 * t)
        voice = voice + buzz
        nyq = 0.5 * sr
        b_lp, a_lp = butter(4, 6500 / nyq, btype='low')
        voice = lfilter(b_lp, a_lp, voice)
    else:
        # Add realistic room acoustic noise floor (-52 dB)
        room_noise = np.random.normal(0, 0.0008, num_samples)
        voice = voice + room_noise

    # Normalize
    max_amp = np.max(np.abs(voice))
    if max_amp > 0:
        voice = (voice / max_amp) * 0.85

    return voice.astype(np.float32)

def generate_all_samples():
    sr = 16000
    samples = [
        {
            "filename": "sample_1_digital_arrest_clone.wav",
            "is_synthetic": True,
            "base_f0": 130.0,
            "duration": 5.5,
            "info": "Synthetic voice clone + Digital arrest scam script"
        },
        {
            "filename": "sample_2_otp_theft_human.wav",
            "is_synthetic": False,
            "base_f0": 160.0,
            "duration": 5.0,
            "info": "Human voice + OTP banking theft script"
        },
        {
            "filename": "sample_3_ai_clone_benign.wav",
            "is_synthetic": True,
            "base_f0": 125.0,
            "duration": 4.5,
            "info": "Synthetic voice clone + Normal legitimate script"
        },
        {
            "filename": "sample_4_legitimate_call.wav",
            "is_synthetic": False,
            "base_f0": 150.0,
            "duration": 5.2,
            "info": "Authentic human voice + Legitimate customer inquiry"
        },
        {
            "filename": "sample_5_hindi_digital_arrest.wav",
            "is_synthetic": True,
            "base_f0": 138.0,
            "duration": 6.0,
            "info": "Synthetic voice clone + Hindi Digital Arrest Police Extortion Call"
        }
    ]

    for item in samples:
        audio = generate_formant_voice(
            duration=item["duration"],
            sr=sr,
            base_f0=item["base_f0"],
            is_synthetic=item["is_synthetic"]
        )
        out_path = os.path.join(SAMPLE_DIR, item["filename"])
        sf.write(out_path, audio, sr)
        print(f"Generated sample: {out_path}")

if __name__ == "__main__":
    generate_all_samples()

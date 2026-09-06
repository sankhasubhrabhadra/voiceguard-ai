import os
import sys
# Add parent dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.audio_processor import AudioProcessor
from app.classifier import VoiceCloneClassifier
from app.scam_detector import ScamDetector
from app.fusion import RiskFusionEngine

def test_pipeline():
    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_audios"))
    processor = AudioProcessor(target_sr=16000)
    classifier = VoiceCloneClassifier()
    detector = ScamDetector()

    test_files = [
        ("sample_1_digital_arrest_clone.wav", "This is Delhi Police Crime Branch regarding money laundering. You are placed under digital arrest.", "High"),
        ("sample_4_legitimate_call.wav", "Hello, I am calling to confirm your delivery order for tomorrow morning.", "Low")
    ]

    for fname, transcript, expected_level in test_files:
        path = os.path.join(sample_dir, fname)
        print(f"\n--- Testing {fname} ---")
        assert os.path.exists(path), f"File {path} not found"
        
        y, sr = processor.load_audio(path)
        features, fvec, raw = processor.extract_features(y, sr)
        spectro, anoms = processor.generate_spectrogram_and_waveform(y, sr)
        print(f"Features: duration={features.duration_seconds}s, pitch={features.mean_pitch_hz}Hz, jitter={features.pitch_jitter_local:.3f}%, shimmer={features.amplitude_shimmer_local:.3f}%")
        
        voice_res = classifier.predict(features, fvec, raw, anoms)
        print(f"Voice Classification: is_cloned={voice_res.is_cloned}, risk_score={voice_res.risk_score}%, confidence={voice_res.confidence}%")
        
        script_res = detector.analyze_transcript(transcript, [])
        print(f"Script Analysis: risk_score={script_res.script_risk_score}%, categories={script_res.detected_categories}, matches={len(script_res.matches)}")
        
        fusion = RiskFusionEngine.fuse(voice_res, script_res)
        print(f"Fused Result: overall={fusion.overall_risk_score}%, level={fusion.risk_level}")
        print(f"Explanation: {fusion.plain_language_explanation}")
        
    print("\n All pipeline tests completed successfully!")

if __name__ == "__main__":
    test_pipeline()

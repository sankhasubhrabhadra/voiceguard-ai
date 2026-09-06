import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.audio_processor import AudioProcessor
from app.classifier import VoiceCloneClassifier
from app.stt_engine import STTEngine
from app.scam_detector import ScamDetector
from app.fusion import RiskFusionEngine

def main():
    test_path = r"C:\Users\Lenovo\Downloads\ai_fraud_call_spoken_demo.wav"
    if not os.path.exists(test_path):
        print("File not found at:", test_path)
        return

    proc = AudioProcessor(target_sr=16000)
    clf = VoiceCloneClassifier()
    stt = STTEngine(model_size="tiny")
    scam = ScamDetector()

    y, sr = proc.load_audio(test_path)
    print(f"Audio loaded: duration={len(y)/sr:.2f}s, sr={sr}")

    stt_res = stt.transcribe(test_path, y=y, sr=sr)
    print("TRANSCRIPT FULL TEXT:\n", repr(stt_res["full_text"]))
    print(f"TRANSCRIPT SEGMENTS: {len(stt_res['segments'])}")
    for s in stt_res["segments"]:
        print(f"  [{s.start_time:.1f} - {s.end_time:.1f}]: {s.text}")

    scam_res = scam.analyze_transcript(stt_res["full_text"], stt_res["segments"])
    print(f"\nSCAM INTENT SCORE: {scam_res.script_risk_score}%")
    print(f"DETECTED CATEGORIES: {scam_res.detected_categories}")
    print(f"MATCHES COUNT: {len(scam_res.matches)}")
    for m in scam_res.matches:
        print(f"  - {m.category}: \"{m.matched_phrase}\" (similarity: {m.similarity_score}%, seed: \"{m.seed_phrase}\")")

    features_obj, fvec, raw_metrics = proc.extract_features(y, sr)
    spectro, anoms = proc.generate_spectrogram_and_waveform(y, sr)
    voice_res = clf.predict(features_obj, fvec, raw_metrics, anoms)
    print(f"\nVOICE RISK SCORE: {voice_res.risk_score}%, IS CLONED: {voice_res.is_cloned}")
    print(f"ANOMALY REGIONS: {[(a.start_time, a.end_time, a.anomaly_type) for a in anoms]}")
    print(f"VOCODER BIOMARKERS: {voice_res.vocoder_biomarkers}")
    print(f"TOP FEATURES: {voice_res.top_contributing_features}")

    fusion_res = RiskFusionEngine.fuse(voice_res, scam_res)
    print(f"\nFUSED RISK SCORE: {fusion_res.overall_risk_score}%, RISK LEVEL: {fusion_res.risk_level}")
    print(f"EXPLANATION: {fusion_res.plain_language_explanation}")
    print(f"SUGGESTED ACTION: {fusion_res.suggested_action}")

if __name__ == "__main__":
    main()

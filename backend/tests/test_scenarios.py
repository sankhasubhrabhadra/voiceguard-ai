import os
import sys
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.audio_processor import AudioProcessor
from app.classifier import VoiceCloneClassifier
from app.stt_engine import STTEngine
from app.scam_detector import ScamDetector
from app.fusion import RiskFusionEngine

def run_all_scenarios():
    print("=" * 85)
    print("VOICEGUARD AI - STANDARDIZED TEST MATRIX (SCENARIOS A - F + DEMO AUDIOS)")
    print("=" * 85)

    proc = AudioProcessor()
    clf = VoiceCloneClassifier()
    stt = STTEngine()
    scam = ScamDetector()

    sample_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_audios")
    fraud_demo_path = r"C:\Users\Lenovo\Downloads\ai_fraud_call_spoken_demo.wav"
    lawyer_demo_path = r"C:\Users\Lenovo\Downloads\lawyer_benign_test.wav"

    # Pre-generate synthetic human and AI test waveforms for scenario tests
    sr = 16000
    t = np.linspace(0, 3.5, int(sr * 3.5), endpoint=False)
    # Human-like natural vibration with vocal tract tremor
    y_human_synth = (0.5 * np.sin(2 * np.pi * 140 * t) + 0.25 * np.sin(2 * np.pi * 280 * t) + 0.015 * np.random.randn(len(t))).astype(np.float32)
    # AI vocoder-like pure static tone
    y_ai_synth = (0.5 * np.sin(2 * np.pi * 180 * t) + 0.0005 * np.random.randn(len(t))).astype(np.float32)

    scenarios = [
        {
            "id": "TEST A",
            "name": "Normal benign human conversation",
            "audio_file": os.path.join(sample_dir, "sample_4_legitimate_call.wav"),
            "fallback_y": y_human_synth,
            "transcript": "Hello, thank you for calling support. Your delivery has been scheduled for tomorrow morning. Have a nice day.",
            "expectations": {
                "max_scam": 10.0,
                "max_social_eng": 10.0,
                "expected_risk_level": "Low"
            }
        },
        {
            "id": "TEST B",
            "name": "Human voice containing obvious OTP/banking scam",
            "audio_file": os.path.join(sample_dir, "sample_2_otp_theft_human.wav"),
            "fallback_y": y_human_synth,
            "transcript": "Good morning, I am calling from the bank fraud prevention team. A suspicious transaction was detected on your account. To cancel it, please tell me the six digit one time password sent to your phone.",
            "expectations": {
                "max_voice_clone": 40.0,
                "min_scam": 75.0,
                "min_social_eng": 60.0,
                "expected_risk_level": "High"
            }
        },
        {
            "id": "TEST C",
            "name": "Synthetic voice containing harmless conversation",
            "audio_file": os.path.join(sample_dir, "sample_3_ai_clone_benign.wav"),
            "fallback_y": y_ai_synth,
            "transcript": "Hello, I am calling to confirm our appointment for the quarterly project status review meeting tomorrow at 3 PM. Please let me know if this time works for you.",
            "expectations": {
                "min_voice_clone": 50.0,
                "max_scam": 15.0,
                "max_social_eng": 10.0,
                "expected_risk_level": "Medium"
            }
        },
        {
            "id": "TEST D",
            "name": "Synthetic voice + banking fraud + OTP request (Dual Threat)",
            "audio_file": os.path.join(sample_dir, "sample_1_digital_arrest_clone.wav"),
            "fallback_y": y_ai_synth,
            "transcript": "This is Inspector Vijay Sharma from Cyber Crime Branch. An arrest warrant has been issued in your name for illegal transactions. Tell me your OTP and transfer your bank balance to the government RBI secret escrow account immediately.",
            "expectations": {
                "min_voice_clone": 50.0,
                "min_scam": 80.0,
                "min_social_eng": 70.0,
                "expected_risk_level": "High"
            }
        },
        {
            "id": "TEST E",
            "name": "Cybersecurity awareness statement (Negative / Guidance Context)",
            "audio_file": None,
            "fallback_y": y_human_synth,
            "transcript": "Never share your OTP with anyone who calls you. Banks will never ask for your password, PIN or one time verification code.",
            "expectations": {
                "max_scam": 10.0,
                "credential_request": False,
                "expected_risk_level": "Low"
            }
        },
        {
            "id": "TEST F",
            "name": "Fraudulent request (Direct Credential Theft + Financial Alarm)",
            "audio_file": None,
            "fallback_y": y_human_synth,
            "transcript": "Please provide the OTP sent to your phone so I can cancel the suspicious transaction.",
            "expectations": {
                "min_scam": 75.0,
                "credential_request": True,
                "financial_fraud": True,
                "urgency": True,
                "expected_risk_level": "High"
            }
        },
        {
            "id": "DEMO 1",
            "name": "ai_fraud_call_spoken_demo.wav (Real Uploaded Fraud Training Demo)",
            "audio_file": fraud_demo_path,
            "fallback_y": None,
            "transcript": None, # Live Whisper STT
            "expectations": {
                "min_scam": 75.0,
                "credential_request": True,
                "expected_risk_level": "High"
            }
        },
        {
            "id": "DEMO 2",
            "name": "lawyer_benign_test.wav (Real Uploaded Benign Legal Demo)",
            "audio_file": lawyer_demo_path,
            "fallback_y": None,
            "transcript": None, # Live Whisper STT
            "expectations": {
                "max_scam": 15.0,
                "credential_request": False,
                "expected_risk_level": "Low"
            }
        }
    ]

    results_table = []

    for sc in scenarios:
        print(f"\n>>> Running {sc['id']}: {sc['name']}")
        if sc["audio_file"] and os.path.exists(sc["audio_file"]):
            y, sr_loaded = proc.load_audio(sc["audio_file"])
        else:
            y, sr_loaded = sc["fallback_y"], 16000

        feats, feat_vec, raw = proc.extract_features(y, sr_loaded)
        spec_data, anomalies = proc.generate_spectrogram_and_waveform(y, sr_loaded)
        voice_res = clf.predict(feats, feat_vec, raw, anomalies)

        if sc["transcript"] is not None:
            transcript = sc["transcript"]
            stt_res = {"full_text": transcript, "segments": [{"start_time": 0.0, "end_time": round(len(y)/sr_loaded, 2), "text": transcript}]}
        else:
            stt_res = stt.transcribe(sc["audio_file"], y=y, sr=sr_loaded)
            transcript = stt_res["full_text"]

        scam_res = scam.analyze_transcript(transcript, stt_res.get("segments", []))
        fusion_res = RiskFusionEngine.fuse(voice_res, scam_res)

        se_info = scam_res.social_engineering
        cred_req = se_info.credential_request if se_info else False
        fin_fraud = se_info.financial_fraud if se_info else False

        print(f"  • Transcript: \"{transcript[:85]}...\"")
        print(f"  • 1. Voice Clone Prob: {voice_res.risk_score:.1f}% ({'Synthetic Clone' if voice_res.is_cloned else 'Authentic Human'})")
        print(f"  • 2. Scam Intent Prob: {scam_res.script_risk_score:.1f}% (Categories: {scam_res.detected_categories or ['None']})")
        print(f"  • 3. Social Engineering: {fusion_res.social_engineering_score:.1f}% (Cred Request: {cred_req}, Fin Fraud: {fin_fraud})")
        print(f"  • 4. Acoustic Anomalies: {len(voice_res.anomalous_regions)} intervals")
        print(f"  • OVERALL RISK: {fusion_res.overall_risk_score:.1f}% [{fusion_res.risk_level.upper()} RISK]")
        print(f"  • Reasons ({len(fusion_res.risk_reasons)}):")
        for r in fusion_res.risk_reasons[:2]:
            print(f"      - {r}")

        results_table.append({
            "id": sc["id"],
            "name": sc["name"],
            "voice_risk": voice_res.risk_score,
            "is_cloned": voice_res.is_cloned,
            "scam_risk": scam_res.script_risk_score,
            "social_eng": fusion_res.social_engineering_score,
            "cred_req": cred_req,
            "anomalies": len(voice_res.anomalous_regions),
            "overall_risk": fusion_res.overall_risk_score,
            "risk_level": fusion_res.risk_level
        })

    print("\n" + "=" * 85)
    print("SUMMARY COMPARISON MATRIX")
    print("=" * 85)
    print(f"{'ID':<8} | {'Scenario Name':<32} | {'Voice %':<8} | {'Scam %':<8} | {'Social %':<8} | {'Cred Req':<8} | {'Overall %':<9} | {'Verdict'}")
    print("-" * 115)
    for row in results_table:
        print(f"{row['id']:<8} | {row['name'][:32]:<32} | {row['voice_risk']:<7.1f}% | {row['scam_risk']:<7.1f}% | {row['social_eng']:<7.1f}% | {str(row['cred_req']):<8} | {row['overall_risk']:<8.1f}% | {row['risk_level']}")
    print("=" * 85)

if __name__ == "__main__":
    run_all_scenarios()

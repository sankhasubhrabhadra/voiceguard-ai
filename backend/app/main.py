import os
import io
import uuid
import hashlib
import logging
import shutil
import tempfile
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.models import (
    AnalyzeAudioResponse,
    VoiceAnalysisResult,
    TranscriptAnalysisResult,
    FusedRiskAssessment,
    CallReportRequest,
    CallReportResponse,
    SampleAudioItem
)
from app.audio_processor import AudioProcessor
from app.classifier import VoiceCloneClassifier
from app.stt_engine import STTEngine
from app.scam_detector import ScamDetector
from app.ollama_analyzer import OllamaAnalyzer
from app.fusion import RiskFusionEngine
from app.database import ReportDatabase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("voiceguard.api")

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_audios")

app = FastAPI(
    title="VoiceGuard AI API",
    description="Real-time Voice Clone and Scam-Call Detection Engine",
    version="2.1.0"
)

# Robust CORS configuration for all frontend environments (Vercel, localhost, tunnels)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

@app.get("/")
def root():
    return {"status": "online", "service": "VoiceGuard AI Forensics API", "version": "2.1.0"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "VoiceGuard AI Forensics API"}

# Initialize singletons
audio_processor = AudioProcessor(target_sr=16000)
classifier = VoiceCloneClassifier()
stt_engine = STTEngine(model_size="base")
scam_detector = ScamDetector()
ollama_analyzer = OllamaAnalyzer()
db = ReportDatabase()

SAMPLE_SCENARIOS = {
    "sample_1_digital_arrest_clone.wav": {
        "id": "sample_1",
        "title": "Digital Arrest Scam (AI Cloned Voice)",
        "category": "Digital Arrest & High Threat",
        "expected_risk": "High",
        "description": "Synthetic voice clone impersonating Mumbai Police / Cyber Crime Branch alleging money laundering via an intercepted FedEx narcotics parcel, enforcing an illegal 'digital arrest'.",
        "default_transcript": "This is Inspector Vijay Sharma from Mumbai Cyber Crime Branch. A FedEx courier parcel containing MDMA drugs and fake passports in your name has been confiscated by customs. You are placed under immediate digital arrest. Do not disconnect this video call or local police will arrive at your address."
    },
    "sample_2_otp_theft_human.wav": {
        "id": "sample_2",
        "title": "OTP & KYC Expiry Fraud (Human Voice)",
        "category": "Banking Credential Theft",
        "expected_risk": "High",
        "description": "Human scammer calling from fake bank fraud department demanding 6-digit OTP code to stop an unauthorized account suspension.",
        "default_transcript": "Good morning, I am calling from the SBI Fraud Prevention Division. Your debit card and net banking KYC has expired and will be blocked today. To verify your identity and stop suspension, please read out the 6-digit OTP verification code sent to your registered mobile."
    },
    "sample_3_ai_clone_benign.wav": {
        "id": "sample_3",
        "title": "AI Voice Clone (Benign Content)",
        "category": "Synthetic Voice Only",
        "expected_risk": "Medium",
        "description": "Cloned AI synthetic voice discussing regular meeting scheduling without fraudulent intent.",
        "default_transcript": "Hello, I am calling to confirm our schedule for the quarterly project status review meeting tomorrow at 3 PM. Please let me know if this time works for you."
    },
    "sample_4_legitimate_call.wav": {
        "id": "sample_4",
        "title": "Legitimate Support Call (Authentic Human)",
        "category": "Safe / Bonafide",
        "expected_risk": "Low",
        "description": "Authentic human conversation from customer support confirming order delivery with no suspicious requests.",
        "default_transcript": "Hello, thank you for contacting customer support. We have received your query regarding the delivery timeline and your package is scheduled to arrive tomorrow morning. Have a wonderful day."
    },
    "sample_5_hindi_digital_arrest.wav": {
        "id": "sample_5",
        "title": "Digital Arrest Extortion Call (Hindi / हिंदी)",
        "category": "Digital Arrest (Hindi)",
        "expected_risk": "High",
        "description": "Synthetic voice impersonating Delhi Police Cyber Crime Branch alleging an intercepted narcotics FedEx courier parcel, enforcing an illegal 'digital arrest' in Hindi.",
        "default_transcript": "यह दिल्ली पुलिस क्राइम ब्रांच से इंस्पेक्टर विजय शर्मा बोल रहे हैं। आपके नाम पर मुंबई कस्टम्स में एक फेडेक्स पार्सल जब्त हुआ है जिसमें गैर-कानूनी ड्रग्स और जाली पासपोर्ट मिले हैं। आपको तुरंत डिजिटल अरेस्ट में रखा गया है। यह वीडियो कॉल बिल्कुल मत काटना नहीं तो पुलिस आपके घर पहुंच जाएगी।"
    },
    "sample_6_hindi_bank_otp_fraud.wav": {
        "id": "sample_6",
        "title": "SBI KYC & OTP Theft Scam (Hindi / हिंदी)",
        "category": "Banking Credential Theft (Hindi)",
        "expected_risk": "High",
        "description": "Scammer calling in Hindi claiming to be from SBI Fraud Prevention Department demanding immediate 6-digit OTP verification to prevent debit card and account blockage.",
        "default_transcript": "नमस्ते, मैं स्टेट बैंक ऑफ इंडिया के फ्रॉड प्रिवेंशन डिपार्टमेंट से बोल रहा हूँ। आपका एटीएम कार्ड और बैंक खाता आज शाम ब्लॉक हो जाएगा क्योंकि केवाईसी एक्सपायर हो गई है। खाता चालू रखने के लिए आपके मोबाइल पर भेजा गया 6 अंकों का ओटीपी वेरिफिकेशन कोड तुरंत बताइए।"
    },
    "sample_7_hindi_legitimate_call.wav": {
        "id": "sample_7",
        "title": "Clinic Appointment Confirmation (Hindi / हिंदी)",
        "category": "Safe / Bonafide (Hindi)",
        "expected_risk": "Low",
        "description": "Authentic Hindi customer conversation confirming doctor appointment with zero suspicious prompts.",
        "default_transcript": "नमस्ते, अपोलो क्लिनिक से बात कर रहे हैं। आपका कल दोपहर 3 बजे डॉक्टर वर्मा के साथ अपॉइंटमेंट कन्फर्म हो गया है। कृपया समय पर क्लिनिक पहुंचें। धन्यवाद।"
    }
}

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "VoiceGuard AI Engine",
        "version": "2.1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/api/samples", response_model=List[SampleAudioItem])
def list_samples():
    """Returns available pre-configured test audio scenarios."""
    items = []
    for filename, meta in SAMPLE_SCENARIOS.items():
        items.append(SampleAudioItem(
            id=meta["id"],
            title=meta["title"],
            category=meta["category"],
            expected_risk=meta["expected_risk"],
            description=meta["description"],
            filename=filename
        ))
    return items

@app.get("/api/samples/{filename}")
def get_sample_audio_file(filename: str):
    """Streams the sample audio file for frontend playback."""
    file_path = os.path.join(SAMPLE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample audio file not found.")
    return FileResponse(file_path, media_type="audio/wav")

@app.post("/api/analyze", response_model=AnalyzeAudioResponse)
def analyze_audio(
    file: Optional[UploadFile] = File(None),
    sample_filename: Optional[str] = Form(None),
    transcript_override: Optional[str] = Form(None)
):
    """
    Main audio analysis pipeline executed per upload:
    1. Generates unique analysis_id and computes SHA-256 audio_hash.
    2. Extracts acoustic & spectral features (MFCC, Jitter, Shimmer, Flatness, Spectrogram).
    3. Classifies voice authenticity (Real vs Cloned) via Random Forest + physical vocoder biomarkers.
    4. Runs Whisper STT for transcript & matches scam-script phrases and behavioral context.
    5. Fuses voice and transcript signals into explainable final risk level.
    """
    analysis_id = str(uuid.uuid4())
    temp_file_path = None
    try:
        # Determine source of audio & compute hash
        if file and file.filename:
            filename = file.filename
            file_bytes = file.file.read()
            audio_hash = hashlib.sha256(file_bytes).hexdigest()
            suffix = os.path.splitext(filename)[1] or ".wav"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                temp_file_path = tmp.name
                tmp.write(file_bytes)
            audio_source = temp_file_path
        elif sample_filename and sample_filename in SAMPLE_SCENARIOS:
            filename = sample_filename
            audio_source = os.path.join(SAMPLE_DIR, sample_filename)
            if not os.path.exists(audio_source):
                raise HTTPException(status_code=404, detail="Selected sample file does not exist.")
            with open(audio_source, "rb") as sf_read:
                audio_hash = hashlib.sha256(sf_read.read()).hexdigest()
        else:
            raise HTTPException(status_code=400, detail="Please provide an audio file or select a valid sample.")

        logger.info(f"[{analysis_id}] INGEST: file='{filename}', sha256={audio_hash[:16]}")

        # Step 1: Acoustic Feature Extraction
        y, sr = audio_processor.load_audio(audio_source)
        features_obj, feature_vector, raw_metrics = audio_processor.extract_features(y, sr)
        spectrogram_data, anomalies = audio_processor.generate_spectrogram_and_waveform(y, sr)

        logger.info(
            f"[{analysis_id}] ACOUSTICS: duration={features_obj.duration_seconds}s, "
            f"samples={len(y)}, sr={sr}, mean_pitch={features_obj.mean_pitch_hz}Hz, "
            f"pitch_std={features_obj.pitch_std}Hz, jitter={features_obj.pitch_jitter_local:.3f}%, "
            f"shimmer={features_obj.amplitude_shimmer_local:.3f}%, silence={features_obj.silence_noise_floor_db}dB"
        )

        # Step 2: Voice Clone ML Classification
        voice_result = classifier.predict(
            features_obj=features_obj,
            feature_vector=feature_vector,
            raw_metrics=raw_metrics,
            anomalies=anomalies
        )
        voice_result.spectrogram_data = spectrogram_data

        logger.info(
            f"[{analysis_id}] CLASSIFIER: voice_risk={voice_result.risk_score:.1f}%, "
            f"is_cloned={voice_result.is_cloned}, confidence={voice_result.confidence:.1f}%, "
            f"vocoder_markers={len(voice_result.vocoder_biomarkers)}, anomalies={len(anomalies)}"
        )

        # Step 3: Transcript Pipeline (Whisper STT + Scam-pattern matching)
        if transcript_override and transcript_override.strip():
            transcript_text = transcript_override.strip()
            stt_result = {
                "full_text": transcript_text,
                "segments": [
                    {
                        "start_time": 0.0,
                        "end_time": round(features_obj.duration_seconds, 2),
                        "text": transcript_text
                    }
                ]
            }
        elif sample_filename and sample_filename in SAMPLE_SCENARIOS:
            preset_text = SAMPLE_SCENARIOS[sample_filename]["default_transcript"]
            stt_result = {
                "full_text": preset_text,
                "segments": [
                    {
                        "start_time": 0.0,
                        "end_time": round(features_obj.duration_seconds, 2),
                        "text": preset_text
                    }
                ]
            }
            transcript_text = preset_text
        else:
            stt_result = stt_engine.transcribe(audio_source, y=y, sr=sr)
            transcript_text = stt_result["full_text"]

        transcript_result = scam_detector.analyze_transcript(
            transcript=transcript_text,
            segments=stt_result.get("segments", []),
            stt_lang=stt_result.get("language")
        )

        # Step 3.5: Optional Local Ollama Cognitive Forensics
        ollama_insight = ollama_analyzer.analyze_transcript(
            transcript=transcript_text,
            voice_risk=voice_result.risk_score
        )
        transcript_result.ollama_insight = ollama_insight

        logger.info(
            f"[{analysis_id}] SCAM DETECTOR: script_risk={transcript_result.script_risk_score:.1f}%, "
            f"categories={transcript_result.detected_categories}, matches={len(transcript_result.matches)}, "
            f"ollama_active={ollama_insight.enabled if ollama_insight else False}"
        )

        # Step 4: Multi-Modal Risk Fusion
        fusion_result = RiskFusionEngine.fuse(
            voice_result=voice_result,
            transcript_result=transcript_result
        )

        logger.info(
            f"[{analysis_id}] FUSION: overall_risk={fusion_result.overall_risk_score:.1f}%, "
            f"level={fusion_result.risk_level}, simulation={fusion_result.is_simulation_detected}"
        )

        # Step 5: Auto-Log Analysis into Audit Store
        try:
            auto_report_id = db.add_report(
                caller_number="Suspect / Intercepted Call",
                audio_filename=filename,
                risk_level=fusion_result.risk_level,
                overall_risk_score=fusion_result.overall_risk_score,
                voice_risk_score=fusion_result.voice_risk_score,
                script_risk_score=fusion_result.script_risk_score,
                transcript_snippet=transcript_text[:220] if transcript_text else "",
                notes=f"Auto-logged. Threat Categories: {', '.join(transcript_result.detected_categories) if transcript_result.detected_categories else 'None detected'}."
            )
            logger.info(f"[{analysis_id}] AUDIT: Saved incident report {auto_report_id}")
        except Exception as audit_err:
            logger.warning(f"Failed to auto-log incident report: {audit_err}")

        return AnalyzeAudioResponse(
            success=True,
            analysis_id=analysis_id,
            audio_hash=audio_hash,
            filename=filename,
            duration=features_obj.duration_seconds,
            sample_rate=sr,
            num_samples=len(y),
            fusion=fusion_result,
            voice_analysis=voice_result,
            transcript_analysis=transcript_result,
            processed_at=datetime.utcnow().isoformat() + "Z"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Audio processing error: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass

@app.post("/api/report", response_model=CallReportResponse)
def report_call(req: CallReportRequest):
    """Logs suspect call details to SQLite/JSON database."""
    report_id = db.add_report(
        caller_number=req.caller_number,
        audio_filename=req.audio_filename,
        risk_level=req.risk_level,
        overall_risk_score=req.overall_risk_score,
        voice_risk_score=req.voice_risk_score,
        script_risk_score=req.script_risk_score,
        transcript_snippet=req.transcript_snippet or "",
        notes=req.notes or ""
    )
    return CallReportResponse(
        success=True,
        report_id=report_id,
        message="Suspect call report recorded successfully.",
        logged_at=datetime.utcnow().isoformat() + "Z"
    )

@app.get("/api/reports")
def get_reports(limit: int = 50):
    """Retrieves list of reported calls."""
    return db.list_reports(limit=limit)

@app.get("/api/status/ollama")
def get_ollama_status():
    """Checks if local Ollama LLM server is accessible."""
    model = ollama_analyzer.get_active_model()
    return {
        "available": model is not None,
        "base_url": ollama_analyzer.base_url,
        "active_model": model,
        "supported_models": ollama_analyzer.preferred_models
    }

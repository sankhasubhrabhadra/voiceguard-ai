# VoiceGuard AI 🛡️

**VoiceGuard AI** is a real-time AI voice clone and scam-call detection platform. It uses multi-modal forensics to analyze physical vocal tract acoustic anomalies in audio calls and detects fraudulent conversational intent patterns in transcribed speech (such as digital arrest, customs/FedEx parcel extortion, OTP theft, and coercive authority intimidation), fusing both modalities into a single explainable risk score.

---

## ⚡ Core Features

1. **Acoustic Vocal Tract Forensics (Librosa + Random Forest)**:
   - Evaluates micro-pitch jitter ($\le 0.18\%$ indicates robotic phase rigidity, $\ge 3.5\%$ indicates vocoder neural synthesis artifacts).
   - Computes amplitude shimmer, spectral flatness (Wiener entropy), high-frequency energy rolloff, and 20 MFCC delta distributions.
   - Outputs top contributing acoustic features for explainability.

2. **Waveform & Spectral Forensics Component**:
   - Visualizes the full acoustic amplitude envelope.
   - Interactive 2D time-frequency Mel-Spectrogram (0 to 8 kHz) with highlighted anomaly artifact zones.

3. **Speech-to-Text & Semantic Scam Script Pipeline**:
   - Local OpenAI Whisper STT for transcript generation.
   - Sentence-Transformers semantic embedding matching against curated fraud clusters:
     - *Digital Arrest & Law Enforcement Impersonation* (Police, CBI, Customs, Supreme Court summons)
     - *OTP & Banking Credential Theft* (KYC renewal, CVV, 6-digit OTP codes)
     - *Urgent Coercion & Escrow Demands* (Immediate fund transfers, non-bailable arrest threats)
     - *Remote Access Device Hijack* (AnyDesk, TeamViewer, screen-sharing APKs)

4. **Multi-Modal Risk Fusion Engine**:
   - Synthesizes `voice_risk_score` (0-100) and `script_risk_score` (0-100) into a single risk level: **Low** (<35%), **Medium** (35-70%), **High** (>70%).
   - Generates natural language explanations and suggested safety actions.

5. **Strict Minimalist Dashboard (React + Tailwind CSS)**:
   - Palette: Near-white background (`#FAFAFA`), near-black text (`#111111`), single muted indigo accent (`#4338CA`), soft 8px corners (`rounded-lg`), subtle card shadows, and risk-conveying indicator badges (Teal / Amber / Deep Red).
   - 4 built-in preset test scenarios for instant one-click demonstration.

6. **Call Incident Reporting & Audit Store**:
   - SQLite / JSON audit log of reported calls with generated reference IDs (`REP-XXXXXX`).

---

## 🏗️ Project Architecture

```
voiceguard-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI server with /api/analyze, /api/samples, /api/report
│   │   ├── models.py                # Pydantic schemas
│   │   ├── audio_processor.py       # Librosa acoustic & spectral feature extractor
│   │   ├── classifier.py            # Random Forest voice clone detector + explainability
│   │   ├── stt_engine.py            # OpenAI Whisper local STT
│   │   ├── scam_detector.py         # Sentence-Transformers semantic script matcher
│   │   ├── fusion.py                # Multi-modal risk fusion & natural language synthesizer
│   │   └── database.py              # SQLite/JSON call incident reporting store
│   ├── sample_audios/               # Pre-generated audio test files
│   ├── tests/
│   │   ├── test_audio_pipeline.py   # Unit tests for librosa & feature pipeline
│   │   └── test_api.py              # Integration tests for all endpoints
│   ├── generate_samples.py          # Synthetic formant audio generator
│   └── run_server.py                # Backend daemon runner
└── frontend/
    ├── src/
    │   ├── App.jsx                  # Main dashboard application
    │   ├── components/
    │   │   ├── Header.jsx           # Minimalist navbar with report badge
    │   │   ├── AudioUploader.jsx    # Drag-and-drop file uploader & player
    │   │   ├── SampleAudioSelector.jsx # Preset scenario selector
    │   │   ├── RiskGauge.jsx        # Circular risk gauge & sub-score bars
    │   │   ├── SpectrogramViewer.jsx# Waveform & Spectrogram with anomaly flags
    │   │   ├── TranscriptViewer.jsx # Whisper transcript with fraud highlights
    │   │   ├── ExplanationSection.jsx # Detailed feature importance breakdown
    │   │   ├── ReportModal.jsx      # Modal to report scam numbers
    │   │   └── ReportedCallsList.jsx# Incident audit drawer
    │   └── services/
    │       └── api.js               # API client
    ├── index.html
    └── package.json
```

---

## 🚀 Getting Started

### 1. Run Backend Server
```bash
cd backend
python -u run_server.py
```
Backend runs at `http://127.0.0.1:8000`.

### 2. Run Frontend
```bash
cd frontend
npm run dev
```
Frontend runs at `http://localhost:5173`.

### 3. Run Automated Tests
```bash
cd backend
python tests/test_api.py
```

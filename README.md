# VoiceGuard AI 🛡️

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19+-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4+-06B6D4?style=flat&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![OpenAI Whisper](https://img.shields.io/badge/STT-OpenAI%20Whisper-orange?style=flat)](https://github.com/openai/whisper)
[![Sentence-Transformers](https://img.shields.io/badge/NLP-Sentence--Transformers-blueviolet?style=flat)](https://sbert.net)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?style=flat&logo=scikitlearn&logoColor=white)](https://scikit-learn.org)

**VoiceGuard AI** is a multi-modal, real-time audio forensics and fraudulent conversational intent detection platform. It is engineered to detect **AI-synthesized/deepfake voice clones** and **coercive scam-call scripts** (e.g., Digital Arrest, Customs/FedEx parcel extortion, OTP theft, and authority impersonation), fusing both signals into an explainable risk score.

---

## 📑 Table of Contents
- [⚡ Key Features](#-key-features)
- [🧠 Detection Architecture](#-detection-architecture)
- [🔬 Forensic Methodology](#-forensic-methodology)
  - [1. Acoustic Vocal Tract Forensics](#1-acoustic-vocal-tract-forensics)
  - [2. Whisper STT & Semantic Intent Engine](#2-whisper-stt--semantic-intent-engine)
  - [3. Multi-Modal Risk Fusion Engine](#3-multi-modal-risk-fusion-engine)
- [📁 Repository Structure](#-repository-structure)
- [🚀 Quickstart Guide](#-quickstart-guide)
  - [Prerequisites](#prerequisites)
  - [1. Backend Setup](#1-backend-setup)
  - [2. Frontend Setup](#2-frontend-setup)
- [📡 API Documentation](#-api-documentation)
- [🧪 Included Test Scenarios](#-included-test-scenarios)
- [🛡️ Incident Reporting & Audit Store](#️-incident-reporting--audit-store)
- [📄 License](#-license)

---

## ⚡ Key Features

- **Micro-Acoustic Voice Clone Detection**: Inspects phase rigidity, vocal tract jitter, amplitude shimmer, Wiener spectral flatness, and 20 MFCC delta statistics via a calibrated Random Forest classifier.
- **Interactive 2D Mel-Spectrogram & Waveform**: Renders amplitude envelopes and time-frequency spectrograms (0–8 kHz) with flagged anomaly zones.
- **Local Neural Speech-to-Text**: High-accuracy local speech transcription powered by OpenAI Whisper (`base`/`small`).
- **Semantic Scam Clustering**: Sentence-Transformers embeddings matched with cosine similarity against high-risk conversational fraud clusters (Digital Arrest, Banking KYC, Urgent Escrow, Remote Access Takeover).
- **Explainable Multi-Modal Risk Synthesis**: Fuses acoustic probabilities with semantic intent scores, generating plain-language reasoning, risk breakdowns, and recommended safety actions.
- **Incident Audit Store**: One-click suspicious call reporting with auto-generated reference IDs (`REP-XXXXXX`) backed by SQLite.
- **Minimalist Cyber-Forensic UI**: Built with React, Tailwind CSS, Lucide icons, and responsive desktop/mobile layouts.

---

## 🧠 Detection Architecture

```
                                  ┌────────────────────────┐
                                  │   Incoming Audio File   │
                                  │   (.wav, .mp3, .m4a)   │
                                  └───────────┬────────────┘
                                              │
                     ┌────────────────────────┴────────────────────────┐
                     ▼                                                 ▼
      ┌─────────────────────────────┐                   ┌─────────────────────────────┐
      │   Acoustic Signal Engine    │                   │   OpenAI Whisper Engine     │
      │  (Librosa Audio Processing) │                   │  (Local Speech-to-Text)     │
      └──────────────┬──────────────┘                   └──────────────┬──────────────┘
                     │                                                 │
          Extracted Feature Vector                             Transcribed Text
     (Jitter, Shimmer, MFCCs, Rolloff)                                 │
                     │                                                 ▼
                     ▼                                  ┌─────────────────────────────┐
      ┌─────────────────────────────┐                   │   Semantic Fraud Matcher    │
      │  Calibrated Random Forest   │                   │   (Sentence-Transformers)   │
      │    Voice Clone Classifier   │                   │  Curated Threat Clusters    │
      └──────────────┬──────────────┘                   └──────────────┬──────────────┘
                     │                                                 │
            Voice Clone Prob %                                 Scam Intent Score %
                     │                                                 │
                     └────────────────────────┬────────────────────────┘
                                              │
                                              ▼
                               ┌─────────────────────────────┐
                               │  Multi-Modal Risk Fusion    │
                               │  • Weighted Risk Score      │
                               │  • Natural Explanations     │
                               │  • Safety Recommendations   │
                               └──────────────┬──────────────┘
                                              │
                                              ▼
                               ┌─────────────────────────────┐
                               │     VoiceGuard UI / API     │
                               └─────────────────────────────┘
```

---

## 🔬 Forensic Methodology

### 1. Acoustic Vocal Tract Forensics
Human vocal folds produce natural micro-perturbations. Neural vocoders (HiFi-GAN, WaveGlow, Diffusion) and voice cloning models leave distinct spectral artifacts:
- **Pitch Jitter**: Voice clones often demonstrate unnatural pitch flatness (<= 0.18%) or vocoder synthesis instability (>= 3.5%).
- **Spectral Flatness (Wiener Entropy)**: Evaluates noise-like vs. tonal distribution across frequency bins.
- **Spectral Rolloff & High-Frequency Cutoff**: Detects synthetic frequency truncations typical of 16kHz/22.05kHz model outputs.
- **MFCC Feature Vector**: 20-band Mel-Frequency Cepstral Coefficients with delta dynamics capturing unnatural formant transitions.

### 2. Whisper STT & Semantic Intent Engine
Transcribes spoken audio into full text and segment-level timestamps. The semantic detector embeds sentences via `all-MiniLM-L6-v2` and calculates maximum semantic similarity across critical scam clusters:
- **Digital Arrest & Law Enforcement**: Impersonation of Police, CBI, Customs, Supreme Court, or narcotics investigations.
- **Banking / OTP Extortion**: Coercive requests for one-time passwords, debit card PINs, CVVs, or KYC re-verification.
- **Urgent Coercion & Escrow**: Demands for instant RTGS/IMPS fund transfers under threat of asset freezing.
- **Remote Access Device Takeover**: Instructions to install screen-sharing software (AnyDesk, TeamViewer).

### 3. Multi-Modal Risk Fusion Engine
Combines acoustic clone probability and semantic script fraud score:
$$\text{Fused Risk Score} = \max\left(P_{clone}, S_{script}, 0.55 \cdot P_{clone} + 0.45 \cdot S_{script}\right)$$
- **LOW RISK (< 35%)**: Natural voice with benign conversation.
- **MEDIUM RISK (35% – 70%)**: Suspicious script patterns or moderate acoustic anomalies.
- **HIGH RISK (> 70%)**: Confirmed synthetic voice clone and/or aggressive fraud vectors.

---

## 📁 Repository Structure

```
voiceguard-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI REST endpoints
│   │   ├── models.py                # Pydantic schemas
│   │   ├── audio_processor.py       # Librosa acoustic & spectral feature extraction
│   │   ├── classifier.py            # Calibrated Random Forest voice clone detector
│   │   ├── rf_voice_model_v3.joblib # Trained acoustic classifier weights
│   │   ├── stt_engine.py            # OpenAI Whisper local STT inference
│   │   ├── scam_detector.py         # Sentence-Transformers semantic intent classifier
│   │   ├── fusion.py                # Multi-modal risk fusion engine
│   │   └── database.py              # SQLite/JSON incident audit database
│   ├── sample_audios/               # 4 pre-packaged test scenario audio files
│   ├── tests/                       # Unit and integration test suites
│   ├── requirements.txt             # Python dependencies
│   ├── run_server.py                # Backend daemon runner
│   └── generate_samples.py          # Synthetic acoustic sample generator
└── frontend/
    ├── src/
    │   ├── App.jsx                  # Main application dashboard
    │   ├── components/
    │   │   ├── Header.jsx           # Top navigation bar
    │   │   ├── AudioUploader.jsx    # Audio upload & interactive player
    │   │   ├── SampleAudioSelector.jsx # One-click demo test scenarios
    │   │   ├── RiskGauge.jsx        # Circular risk score gauge & sub-score bars
    │   │   ├── SpectrogramViewer.jsx# Waveform & Mel-Spectrogram with anomaly flags
    │   │   ├── TranscriptViewer.jsx # Whisper transcript with fraud highlights
    │   │   ├── ExplanationSection.jsx # Explainability & forensic feature importance
    │   │   ├── ReportModal.jsx      # Incident reporting dialog
    │   │   └── ReportedCallsList.jsx# Incident audit trail viewer
    │   └── services/
    │       └── api.js               # Frontend API client
    ├── package.json
    ├── tailwind.config.js
    └── vite.config.js
```

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python**: 3.10+
- **Node.js**: 18+ and npm
- **FFmpeg**: Required for audio decoding (librosa & whisper)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
python -u run_server.py
```
> The backend server starts at **`http://127.0.0.1:8000`**. Interactive Swagger API docs are available at **`http://127.0.0.1:8000/docs`**.

### 2. Frontend Setup

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```
> The dashboard will be available at **`http://localhost:5173`**.

---

## 📡 API Documentation

### `POST /api/analyze`
Accepts an audio file and executes the complete multi-modal forensic pipeline.
- **Request**: `multipart/form-data` (`file: audio/*`)
- **Response**:
```json
{
  "voice_authenticity": {
    "clone_probability": 0.885,
    "classification": "AI Cloned Voice",
    "jitter": 0.0012,
    "shimmer": 0.082,
    "spectral_flatness": 0.0094,
    "top_features": [
      { "name": "Pitch Jitter", "value": 0.0012, "importance": 0.28, "interpretation": "Unnatural pitch rigidity" }
    ]
  },
  "scam_analysis": {
    "script_risk_score": 92.4,
    "classification": "High Risk Scam",
    "transcript": "This is Officer Sharma from Delhi Police Cyber Cell...",
    "detected_patterns": ["Digital Arrest Threat", "Immediate Escrow Transfer"]
  },
  "overall_risk_score": 89.2,
  "overall_risk_level": "HIGH RISK",
  "explanation": "High confidence AI voice synthesis combined with coercive legal intimidation.",
  "recommended_actions": [
    "Do not transfer funds or share any credentials.",
    "Law enforcement agencies never conduct digital arrests over video/voice calls."
  ]
}
```

### `GET /api/samples`
Returns the metadata list of available pre-packaged test scenario audio files.

### `GET /api/samples/{filename}`
Streams the audio file for the specified demo sample.

### `POST /api/report`
Saves an incident report to the audit database and returns a confirmation with a tracking reference ID (`REP-XXXXXX`).

### `GET /api/reports`
Fetches all stored incident audit reports.

---

## 🧪 Included Test Scenarios

VoiceGuard AI comes with 4 pre-configured test scenarios to verify both modalities:

1. **Digital Arrest Scam (AI Voice Clone)**: High clone probability (88.5%) + High scam intent (92.4%) -> **HIGH RISK**
2. **OTP Theft / Banking Scam (Human Voice)**: Low clone probability (12.3%) + High scam intent (89.1%) -> **HIGH RISK**
3. **AI Clone Voice (Benign Script)**: High clone probability (88.5%) + Low scam intent (4.0%) -> **MEDIUM RISK**
4. **Legitimate Doctor Appointment Call**: Low clone probability (5.1%) + Low scam intent (2.0%) -> **LOW RISK**

---

## 🛡️ Incident Reporting & Audit Store

When a fraudulent call is analyzed, users can immediately file an incident report:
- Caller Phone Number
- Threat Category (Digital Arrest, OTP Theft, Extortion, AI Impersonation)
- Incident Notes & Auto-Attached Risk Forensics
- Generates Unique Reference ID (`REP-XXXXXX`) stored in local SQLite.

---

## 📄 License

This project is licensed under the MIT License.

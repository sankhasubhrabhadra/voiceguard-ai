from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AudioAcousticFeatures(BaseModel):
    duration_seconds: float
    sample_rate: int
    mean_pitch_hz: float
    pitch_std: float
    pitch_jitter_local: float
    amplitude_shimmer_local: float
    spectral_flatness_mean: float
    spectral_centroid_mean: float
    spectral_rolloff_mean: float
    zero_crossing_rate_mean: float
    mfcc_means: List[float]
    high_frequency_energy_ratio: float
    harmonic_to_noise_ratio_db: float
    spectral_contrast_mean: Optional[List[float]] = []
    spectral_flux_mean: Optional[float] = 0.0
    pitch_acceleration_variance: Optional[float] = 0.0
    silence_noise_floor_db: Optional[float] = -60.0
    vocoder_artifact_score: Optional[float] = 0.0

class AnomalyRegion(BaseModel):
    start_time: float
    end_time: float
    anomaly_type: str
    confidence: float
    description: str

class AcousticAnomalySummary(BaseModel):
    total_anomalies: int = 0
    anomaly_score: float = 0.0
    anomaly_types: List[str] = []
    regions: List[AnomalyRegion] = []

class VoiceAnalysisResult(BaseModel):
    is_cloned: bool
    confidence: float = Field(..., ge=0.0, le=100.0)
    risk_score: float = Field(..., ge=0.0, le=100.0) # 0 = authentic human, 100 = synthetic clone
    top_contributing_features: List[Dict[str, Any]]
    features: AudioAcousticFeatures
    vocoder_biomarkers: Optional[List[Dict[str, Any]]] = []
    spectrogram_data: Optional[Dict[str, Any]] = None
    anomalous_regions: List[AnomalyRegion] = []
    anomaly_summary: Optional[AcousticAnomalySummary] = None

class TranscriptSegment(BaseModel):
    start_time: float
    end_time: float
    text: str
    is_scam_highlighted: bool = False
    matched_phrases: List[str] = []
    role_tag: Optional[str] = "General" # "Attacker Request", "Victim Refusal", "Educational Note", "General"

class ScamPatternMatch(BaseModel):
    category: str
    matched_phrase: str
    seed_phrase: str
    similarity_score: float
    severity_weight: float
    description: str

class SocialEngineeringDetails(BaseModel):
    score: float = Field(0.0, ge=0.0, le=100.0)
    scam_probability: float = 0.0
    credential_request: bool = False
    financial_fraud: bool = False
    impersonation: bool = False
    urgency: bool = False
    social_engineering: bool = False
    sensitive_information_request: bool = False
    defensive_refusal_detected: bool = False
    educational_context_detected: bool = False
    is_educational_simulation: bool = False
    flagged_intents: List[str] = []
    evidence: List[str] = []

class OllamaInsight(BaseModel):
    enabled: bool = False
    model_name: Optional[str] = None
    threat_summary: Optional[str] = None
    psychological_tactics: List[str] = []
    recommended_defense: Optional[str] = None

class TranscriptAnalysisResult(BaseModel):
    full_transcript: str
    detected_language: Optional[str] = "en"
    script_risk_score: float = Field(..., ge=0.0, le=100.0)
    detected_categories: List[str]
    matches: List[ScamPatternMatch]
    segments: List[TranscriptSegment]
    social_engineering: Optional[SocialEngineeringDetails] = None
    ollama_insight: Optional[OllamaInsight] = None

class FusedRiskAssessment(BaseModel):
    overall_risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_level: str # "Low", "Medium", "High"
    plain_language_explanation: str
    voice_risk_score: float
    script_risk_score: float
    social_engineering_score: float = 0.0
    acoustic_anomaly_score: float = 0.0
    risk_components: Optional[Dict[str, Any]] = None
    key_verdicts: List[str]
    risk_reasons: List[str] = []
    suggested_action: str
    is_simulation_detected: bool = False

class AnalyzeAudioResponse(BaseModel):
    success: bool
    analysis_id: str
    audio_hash: str
    filename: str
    duration: float
    sample_rate: int
    num_samples: int
    fusion: FusedRiskAssessment
    voice_analysis: VoiceAnalysisResult
    transcript_analysis: TranscriptAnalysisResult
    processed_at: str

class CallReportRequest(BaseModel):
    caller_number: Optional[str] = "Unknown"
    audio_filename: str
    risk_level: str
    overall_risk_score: float
    voice_risk_score: float
    script_risk_score: float
    transcript_snippet: Optional[str] = ""
    notes: Optional[str] = ""
    timestamp: Optional[str] = None

class CallReportResponse(BaseModel):
    success: bool
    report_id: str
    message: str
    logged_at: str

class SampleAudioItem(BaseModel):
    id: str
    title: str
    category: str
    expected_risk: str
    description: str
    filename: str

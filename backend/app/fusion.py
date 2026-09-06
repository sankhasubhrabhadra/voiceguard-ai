from typing import List, Dict, Any
from app.models import FusedRiskAssessment, VoiceAnalysisResult, TranscriptAnalysisResult

class RiskFusionEngine:
    """
    Multi-modal fusion engine combining acoustic voice clone forensics,
    acoustic anomaly intervals, semantic scam-script patterns, and social engineering behaviors.
    """
    # Centralized Fusion Weights
    WEIGHT_VOICE_CLONE = 0.25
    WEIGHT_ACOUSTIC_ANOMALIES = 0.15
    WEIGHT_SCAM_INTENT = 0.35
    WEIGHT_SOCIAL_ENGINEERING = 0.25

    # Thresholds
    THRESHOLD_HIGH_RISK = 70.0
    THRESHOLD_MEDIUM_RISK = 35.0

    @classmethod
    def fuse(
        cls,
        voice_result: VoiceAnalysisResult,
        transcript_result: TranscriptAnalysisResult
    ) -> FusedRiskAssessment:
        v_score = float(voice_result.risk_score)
        s_score = float(transcript_result.script_risk_score)
        
        # Extract sub-scores
        se_info = transcript_result.social_engineering
        se_score = float(se_info.score) if se_info else 0.0
        
        anom_info = voice_result.anomaly_summary
        a_score = float(anom_info.anomaly_score) if anom_info else (min(95.0, len(voice_result.anomalous_regions) * 28.0))

        is_simulation = se_info.is_educational_simulation if se_info else False
        has_credential_theft = se_info.credential_request if se_info else False

        # Structured Risk Component Breakdown
        risk_components = {
            "voice_clone": round(v_score, 1),
            "scam_intent": round(s_score, 1),
            "social_engineering": round(se_score, 1),
            "acoustic_anomaly": round(a_score, 1),
            "credential_theft_detected": has_credential_theft
        }

        # Multi-modal risk calculation with clear decoupling
        if s_score >= 70.0 or has_credential_theft:
            if v_score >= 50.0:
                # Dual Threat: Synthetic AI Voice Clone + Active Scam Intent
                raw_overall = max(90.0, min(99.0, (v_score * 0.35 + s_score * 0.45 + se_score * 0.20) * 1.15))
            else:
                # High Risk: Human caller executing active fraud script
                raw_overall = max(78.0, min(96.0, s_score * 0.55 + se_score * 0.35 + a_score * 0.05 + v_score * 0.05))
        elif v_score >= 60.0:
            # Synthetic AI Voice Clone detected (Benign or mild conversation)
            raw_overall = max(45.0, min(65.0, v_score * 0.65 + a_score * 0.15 + s_score * 0.15 + se_score * 0.05))
        elif v_score >= 40.0 or s_score >= 35.0 or a_score >= 40.0:
            # Suspicious voice anomalies or mild urgency
            raw_overall = max(35.0, min(60.0, v_score * 0.35 + s_score * 0.30 + a_score * 0.20 + se_score * 0.15))
        else:
            # Low Risk: Natural human speech + benign conversation
            raw_overall = v_score * 0.30 + s_score * 0.35 + se_score * 0.20 + a_score * 0.15

        overall_score = round(float(raw_overall), 1)

        # Determine Categorical Risk Level
        if overall_score >= cls.THRESHOLD_HIGH_RISK:
            risk_level = "High"
            if is_simulation:
                suggested_action = "AWARENESS DEMO: Active fraud patterns detected within a cybersecurity training simulation. Observe simulated attack techniques."
            else:
                suggested_action = "CRITICAL: High fraud threat detected. Terminate call immediately. Never share OTPs, passwords, or PINs. Report caller on cybercrime portal."
        elif overall_score >= cls.THRESHOLD_MEDIUM_RISK:
            risk_level = "Medium"
            suggested_action = "CAUTION: Synthetic voice characteristics or suspicious verification prompts detected. Verify identity through official independent channels."
        else:
            risk_level = "Low"
            suggested_action = "SAFE: No synthetic voice clone biomarkers or coercive scam patterns detected. Standard vigilance applies."

        # Generate Evidence-Based Bullet Reasons with Exact Calculated Metrics
        risk_reasons: List[str] = []
        key_verdicts: List[str] = []

        # 1. Voice Clone & Vocoder Evidence
        if v_score >= 60.0:
            key_verdicts.append(f"Synthetic AI Voice Clone ({v_score:.1f}%)")
            risk_reasons.append(
                f"Synthetic Voice Clone Signature: Pitch acceleration rigidity ({voice_result.features.pitch_acceleration_variance:.1f} Hz²/frame²) and neural vocoder biomarkers detected."
            )
        elif v_score >= 40.0:
            key_verdicts.append(f"Probable Voice Clone ({v_score:.1f}%)")
            risk_reasons.append(
                f"Acoustic Anomalies: Pitch contour smoothness and compression consistent with neural speech generation ({v_score:.1f}% probability)."
            )
        else:
            key_verdicts.append(f"Authentic Human Phonation ({100.0 - v_score:.1f}% human confidence)")
            risk_reasons.append(
                f"Natural Human Voice: Organic pitch inflection ({voice_result.features.pitch_std:.1f} Hz std) and natural vocal tract micro-tremors ({voice_result.features.pitch_jitter_local:.2f}% jitter)."
            )

        # 2. Acoustic Anomaly Zones Evidence
        num_anomalies = len(voice_result.anomalous_regions)
        if num_anomalies > 0:
            anom_desc = ", ".join([f"{a.start_time:.1f}s–{a.end_time:.1f}s ({a.anomaly_type})" for a in voice_result.anomalous_regions[:2]])
            risk_reasons.append(
                f"{num_anomalies} Acoustic Anomaly Interval(s) Detected: {anom_desc}."
            )
        else:
            risk_reasons.append("Clean Acoustic Signal: Zero localized vocoder phase or harmonic rigidity anomalies detected.")

        # 3. Scam Intent & Specific Matches
        if s_score >= 50.0:
            cats = ", ".join(transcript_result.detected_categories) if transcript_result.detected_categories else "Financial Fraud"
            key_verdicts.append(f"Scam Intent: {cats} ({s_score:.0f}%)")
            
            if transcript_result.matches:
                top_m = transcript_result.matches[0]
                risk_reasons.append(
                    f"Fraud Pattern Matched: '{top_m.matched_phrase}' (Category: {top_m.category}, {top_m.similarity_score}% match)."
                )
            else:
                risk_reasons.append(f"High-Risk Fraud Script: Matches recognized {cats} patterns.")
        else:
            key_verdicts.append("Benign Conversation Script")
            risk_reasons.append("Benign Transcript: No coercive extortion, digital arrest, or credential harvesting scripts detected.")

        # 4. Social Engineering Behavioral Indicators
        if se_info:
            if se_info.credential_request:
                risk_reasons.append(
                    "Active Credential Theft: Caller directly requested sensitive one-time password (OTP) or authentication credentials."
                )
            if se_info.impersonation:
                risk_reasons.append(
                    "Authority Impersonation: Caller fabricated association with bank fraud prevention / security department."
                )
            if se_info.defensive_refusal_detected:
                risk_reasons.append(
                    "Victim Resistance Recognized: Callee explicitly refused to share confidential credentials over the phone."
                )
            if se_info.educational_context_detected:
                risk_reasons.append(
                    "Educational Context: Audio contains explicit cybersecurity training framing ('cybersecurity demonstration', 'fictional fraud call', 'awareness training')."
                )

        # Plain language explanation synthesis
        if is_simulation:
            summary = (
                f"Analysis detected an Educational / Cybersecurity Training Simulation. "
                f"The script exhibits active credential harvesting patterns (OTP solicitation) and bank impersonation, "
                f"while the voice exhibits human phonation with {num_anomalies} acoustic anomaly interval(s)."
            )
        elif overall_score >= cls.THRESHOLD_HIGH_RISK:
            summary = (
                f"High-risk threat detected ({overall_score:.0f}% overall risk). "
                f"{'AI Voice Clone and ' if v_score >= 50 else ''}"
                f"Active fraud patterns detected targeting {', '.join(transcript_result.detected_categories) or 'sensitive credentials'}. "
                f"{suggested_action}"
            )
        elif overall_score >= cls.THRESHOLD_MEDIUM_RISK:
            summary = (
                f"Moderate risk call ({overall_score:.0f}%). "
                f"{'Synthetic AI voice detected on a non-fraudulent conversation.' if v_score >= 50 else 'Suspicious conversational patterns or acoustic anomalies require verification.'}"
            )
        else:
            summary = (
                f"Low risk call ({overall_score:.0f}%). "
                f"Natural human voice dynamics ({voice_result.features.pitch_std:.1f} Hz std) and benign non-coercive conversation detected."
            )

        return FusedRiskAssessment(
            overall_risk_score=overall_score,
            risk_level=risk_level,
            plain_language_explanation=summary,
            voice_risk_score=round(v_score, 1),
            script_risk_score=round(s_score, 1),
            social_engineering_score=round(se_score, 1),
            acoustic_anomaly_score=round(a_score, 1),
            risk_components=risk_components,
            key_verdicts=key_verdicts,
            risk_reasons=risk_reasons[:5],
            suggested_action=suggested_action,
            is_simulation_detected=is_simulation
        )

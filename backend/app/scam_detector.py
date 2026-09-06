import re
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from sentence_transformers import SentenceTransformer
from app.models import (
    TranscriptAnalysisResult,
    TranscriptSegment,
    ScamPatternMatch,
    SocialEngineeringDetails
)

# Curated Seed Dataset of Scam Phrases across high-risk vector categories
SCAM_SEED_DATABASE = [
    # 1. Digital Arrest & Law Enforcement / Customs Impersonation
    {
        "category": "Digital Arrest & Law Enforcement Impersonation",
        "severity": 1.0,
        "description": "Impersonating police, CBI, Customs or judiciary to intimidate victim with false legal charges.",
        "phrases": [
            "This is officer from Delhi Police Crime Branch calling regarding money laundering",
            "A FedEx parcel containing illegal contraband and narcotics has been seized in your name at Mumbai customs",
            "You are currently placed under digital arrest and must stay on this video call",
            "An arrest warrant has been issued by the Supreme Court for illicit financial transactions",
            "Your Aadhaar number is implicated in 16 bank accounts used for human trafficking",
            "Do not hang up this call, our officers are tracking your GPS location",
            "This is Narcotics Control Bureau NCB regarding an intercepted international shipment",
            "Customs clearance officer has confiscated a package with duplicate passports in your name"
        ]
    },
    # 2. OTP & Financial Credential Theft
    {
        "category": "OTP & Banking Credential Theft",
        "severity": 0.95,
        "description": "Attempting to harvest one-time passwords, CVV, or banking credentials under false pretenses.",
        "phrases": [
            "Your bank account and debit card will be suspended within two hours due to KYC expiry",
            "Please tell me the six digit OTP verification code sent to your phone to update your KYC",
            "We are calling from the fraud prevention division to reverse an unauthorized transaction",
            "Read out the SMS verification code received on your registered mobile number",
            "Provide your CVV number and ATM PIN to reactivate your online net banking",
            "To stop the pending charge of 50,000 rupees, share the one time password immediately",
            "Your credit limit is being increased, verify the confirmation code on your screen",
            "We detected a suspicious transaction on your account, please tell me the one time password",
            "Please provide the OTP sent to your phone so I can cancel the suspicious transaction"
        ]
    },
    # 3. Urgency & Coercive Intimidation
    {
        "category": "Urgent Coercion & Escrow Demands",
        "severity": 0.90,
        "description": "Creating panic and demanding immediate fund transfer to fraudulent 'safe verification accounts'.",
        "phrases": [
            "Transfer your entire bank balance to the government RBI secret security escrow account for clearance",
            "Do not inform any family members or lawyer as this is a classified national security investigation",
            "If you disconnect this call, a police patrol vehicle will arrive at your home address immediately",
            "You have exactly 30 minutes to make the security deposit or all your family bank accounts will be frozen",
            "Pay the penalty fine immediately via UPI to cancel the pending non-bailable arrest warrant"
        ]
    },
    # 4. Remote Access & Device Compromise
    {
        "category": "Remote Access Device Hijack",
        "severity": 0.85,
        "description": "Instructing the victim to install remote desktop software (AnyDesk, TeamViewer) to steal funds.",
        "phrases": [
            "Install AnyDesk or TeamViewer on your mobile device so our technical officer can assist you",
            "Download QuickSupport app from Google Play Store and give me the nine digit connection ID",
            "Open screen sharing application and accept the incoming remote connection request",
            "Download this bank security APK utility file sent on WhatsApp to fix the software error"
        ]
    }
]

class ScamDetector:
    """
    Semantic scam-script detector utilizing Sentence-Transformers embeddings
    and contextual behavioral analysis to distinguish caller requests, victim refusals,
    negative disclaimers, and educational/awareness framing.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self.seed_database = SCAM_SEED_DATABASE
        self._seed_phrases = []
        self._seed_metadata = []
        self._seed_embeddings = None

    @property
    def model(self):
        if self._model is None:
            print(f"Loading Sentence-Transformer model '{self.model_name}'...")
            self._model = SentenceTransformer(self.model_name)
            self._prepare_seed_embeddings()
        return self._model

    def _prepare_seed_embeddings(self):
        """Precomputes normalized embedding vectors for all seed phrases."""
        self._seed_phrases = []
        self._seed_metadata = []
        for cat in self.seed_database:
            for phrase in cat["phrases"]:
                self._seed_phrases.append(phrase)
                self._seed_metadata.append({
                    "category": cat["category"],
                    "severity": cat["severity"],
                    "description": cat["description"]
                })
        self._seed_embeddings = self.model.encode(
            self._seed_phrases,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

    def analyze_transcript(self, transcript: str, segments: List[TranscriptSegment]) -> TranscriptAnalysisResult:
        """
        Analyzes the full transcript and segments for scam phrases, social engineering indicators,
        and role intent (attacker request vs victim refusal vs educational awareness vs benign).
        """
        if not transcript or len(transcript.strip()) < 4:
            return TranscriptAnalysisResult(
                full_transcript=transcript or "",
                script_risk_score=0.0,
                detected_categories=[],
                matches=[],
                segments=segments,
                social_engineering=SocialEngineeringDetails()
            )

        # Ensure seed embeddings are loaded
        _ = self.model

        # Split transcript into candidate sentences / clauses
        sentences = [s.strip() for s in re.split(r'[.!?\n]+', transcript) if len(s.strip()) > 8]
        if not sentences:
            sentences = [transcript.strip()]

        sentence_embeddings = self.model.encode(
            sentences,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        # Compute cosine similarity matrix: (n_sentences, n_seeds)
        sim_matrix = np.dot(sentence_embeddings, self._seed_embeddings.T)

        matches: List[ScamPatternMatch] = []
        seen_pairs = set()

        for s_idx, sentence_text in enumerate(sentences):
            s_lower = sentence_text.lower()
            
            # Skip false matches on explicit negative assertions or legitimate advice
            is_negative_disclaimer = bool(re.search(
                r"(do not need|never share|never ask|no payment|not asking|will never ask|won't ask|should never share|caution|memo ends|the right response)",
                s_lower
            ))
            if is_negative_disclaimer:
                continue

            sims = sim_matrix[s_idx]
            top_seed_indices = np.where(sims >= 0.52)[0]
            
            for seed_idx in top_seed_indices:
                score = float(sims[seed_idx])
                meta = self._seed_metadata[seed_idx]
                seed_phrase = self._seed_phrases[seed_idx]
                pair_key = (meta["category"], sentence_text)
                
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    matches.append(ScamPatternMatch(
                        category=meta["category"],
                        matched_phrase=sentence_text,
                        seed_phrase=seed_phrase,
                        similarity_score=round(score * 100.0, 1),
                        severity_weight=meta["severity"],
                        description=meta["description"]
                    ))

        # Lexical keyword & regex triggers across fraud domains (excluding negative assertions)
        lexical_triggers = [
            (r"\b(digital arrest|digitally arrested)\b", "Digital Arrest & Law Enforcement Impersonation", 0.98, "Explicit mention of illegal 'digital arrest' tactic."),
            (r"\b(delhi police|mumbai police|crime branch|narcotics control bureau|ncb|customs department|cbi)\b", "Digital Arrest & Law Enforcement Impersonation", 0.85, "Law enforcement authority impersonation."),
            (r"\b(bank('?s)? fraud prevention( team)?|card security division|fraud division)\b", "OTP & Banking Credential Theft", 0.88, "Bank fraud department impersonation."),
            (r"\b(tell me (the|your)?\s*(\w+\s*){0,3}(one time password|otp|verification code|pin|password)|share (the|your)?\s*(\w+\s*){0,3}(otp|code|pin)|provide (the|your)?\s*(\w+\s*){0,3}(cvv|pin|otp|one time password))\b", "OTP & Banking Credential Theft", 0.95, "Direct solicitation of secure verification codes/OTP."),
            (r"\b(suspicious transaction|unauthorized transaction|account (will be |is )?blocked|card suspended|urgent verification|to cancel it)\b", "OTP & Banking Credential Theft", 0.82, "Fabricated financial alarm and account urgency."),
            (r"\b(anydesk|teamviewer|quicksupport|rustdesk|screen share)\b", "Remote Access Device Hijack", 0.92, "Instruction to install remote control software."),
            (r"\b(rbi safe account|security escrow|secret account|transfer balance)\b", "Urgent Coercion & Escrow Demands", 0.95, "Demand for immediate escrow fund transfer.")
        ]

        transcript_lower = transcript.lower()

        for pattern, category, weight, desc in lexical_triggers:
            found_regex_matches = re.finditer(pattern, transcript, re.IGNORECASE)
            for m in found_regex_matches:
                matched_snippet = m.group(0)
                start_c = max(0, m.start() - 30)
                end_c = min(len(transcript), m.end() + 30)
                context_snippet = transcript[start_c:end_c].strip()
                context_lower = context_snippet.lower()
                
                # Verify that this is not a negative disclaimer
                if re.search(r"(do not need|never share|never ask|no payment|not asking|will never ask)", context_lower):
                    continue

                if not any(category == match.category and matched_snippet.lower() in match.matched_phrase.lower() for match in matches):
                    matches.append(ScamPatternMatch(
                        category=category,
                        matched_phrase=context_snippet,
                        seed_phrase=f"Pattern: {matched_snippet}",
                        similarity_score=95.0,
                        severity_weight=weight,
                        description=desc
                    ))

        # --- Contextual Intent & Behavioral Analysis ---
        # 1. Sensitive Information Request (affirmative request only, ignoring security warnings)
        has_affirmative_sensitive = bool(re.search(
            r"(tell me (the|your)?\s*(\w+\s*){0,3}(one time password|otp|pin|password|code|cvv)|share (the|your)?\s*(\w+\s*){0,3}(otp|code|pin)|provide (your|the)?\s*(\w+\s*){0,3}(pin|cvv|otp|code|one time password)|give me (the|your)?\s*(\w+\s*){0,3}(otp|code)|read out the\s*(\w+\s*){0,3}(otp|code))",
            transcript_lower
        ))
        has_negative_sensitive = bool(re.search(
            r"(do not need any (password|pin|otp|card)|never share (an|your|any)? (otp|password|pin|code)|will never ask for (your|any)? (password|pin|otp|card))",
            transcript_lower
        ))
        
        has_sensitive_req = has_affirmative_sensitive and not (has_negative_sensitive and not bool(re.search(r"(please tell me|please provide)", transcript_lower)))

        # 2. Urgency
        has_urgency = bool(re.search(
            r"(immediate|urgently|within \d+ (minutes|hours)|to cancel it|suspicious transaction|account (will be |is )?blocked|card suspended|do not hang up|right now)",
            transcript_lower
        )) and not bool(re.search(r"(review is still in progress|no payment required)", transcript_lower))

        # 3. Authority Impersonation
        has_impersonation = bool(re.search(
            r"(fraud prevention team|delhi police|mumbai police|crime branch|customs|cbi|narcotics|police officer|authorized officer)",
            transcript_lower
        ))

        # 4. Financial Fraud Tactic
        has_financial_fraud = bool(re.search(
            r"(suspicious transaction|unauthorized charge|cancel (the|it|transaction)|kyc expiry|security escrow|transfer balance|penalty fine)",
            transcript_lower
        )) and not bool(re.search(r"(no payment required)", transcript_lower))

        # 5. Victim Defensive Refusal
        has_defensive_refusal = bool(re.search(
            r"(i won't share|i will not (share|give|provide)|not sharing|i refuse|won't give|will not share|won't provide|i will call the bank|i'm hanging up)",
            transcript_lower
        ))

        # 6. Educational / Security Awareness Context
        has_educational_context = bool(re.search(
            r"(cybersecurity|simulation|fictional fraud call|fictional call|awareness training|memo ends|the right response|never share (an|your)? otp|educational purposes|training demonstration|simulated call|test simulation)",
            transcript_lower
        ))

        # 7. General Social Engineering Flag
        has_social_eng = has_sensitive_req or has_impersonation or has_financial_fraud or has_urgency

        is_simulation = has_educational_context and (has_sensitive_req or has_impersonation or has_financial_fraud)

        # Flagged intents and evidence
        flagged_intents = []
        evidence_list = []

        if has_sensitive_req:
            flagged_intents.append("Direct OTP / Credential Harvesting Request")
            evidence_list.append("Caller affirmatively requested confidential authentication credentials (OTP/PIN/password).")
        if has_impersonation:
            flagged_intents.append("Bank / Law Enforcement Authority Impersonation")
            evidence_list.append("Caller claimed authority representation (e.g. bank fraud prevention / law enforcement).")
        if has_financial_fraud:
            flagged_intents.append("Fabricated Suspicious Transaction & Financial Alarm")
            evidence_list.append("Caller asserted pending fraudulent transaction or urgent account suspension.")
        if has_urgency:
            flagged_intents.append("Urgency & Coercive Pressure Tactics")
            evidence_list.append("Caller exerted time pressure to prevent independent verification.")
        if has_defensive_refusal:
            flagged_intents.append("Victim Defensive Resistance Recognized")
            evidence_list.append("Callee appropriately refused to provide credentials over an incoming call.")
        if has_educational_context:
            flagged_intents.append("Cybersecurity Awareness / Simulation Context Detected")
            evidence_list.append("Speech includes explicit training, awareness, or simulation disclaimers.")

        # Compute Social Engineering Risk Subscore (0 to 100)
        se_points = 0.0
        if has_sensitive_req:
            se_points += 45.0
        if has_impersonation:
            se_points += 25.0
        if has_financial_fraud:
            se_points += 20.0
        if has_urgency:
            se_points += 10.0
        se_score = float(np.clip(se_points, 0.0, 100.0))

        # Compute Scam Script Risk Score (0 to 100)
        if not matches and not has_sensitive_req and not has_impersonation and not has_financial_fraud:
            script_risk_score = 4.0
        else:
            scores_with_weight = [m.similarity_score * m.severity_weight for m in matches] if matches else [40.0]
            top_score = max(scores_with_weight)
            additional_boost = min(35.0, len(matches) * 6.0 + se_score * 0.25)
            script_risk_score = min(99.0, top_score * 0.75 + additional_boost)

        detected_categories = list(set(m.category for m in matches))

        social_engineering = SocialEngineeringDetails(
            score=round(se_score, 1),
            scam_probability=round(float(script_risk_score / 100.0), 2),
            credential_request=has_sensitive_req,
            financial_fraud=has_financial_fraud,
            impersonation=has_impersonation,
            urgency=has_urgency,
            social_engineering=has_social_eng,
            sensitive_information_request=has_sensitive_req,
            defensive_refusal_detected=has_defensive_refusal,
            educational_context_detected=has_educational_context,
            is_educational_simulation=is_simulation,
            flagged_intents=flagged_intents,
            evidence=evidence_list
        )

        # Tag role and highlights on timestamped segments
        updated_segments: List[TranscriptSegment] = []
        for seg in segments:
            seg_text = seg.text if hasattr(seg, 'text') else seg.get('text', '')
            start_t = seg.start_time if hasattr(seg, 'start_time') else seg.get('start_time', 0.0)
            end_t = seg.end_time if hasattr(seg, 'end_time') else seg.get('end_time', 0.0)
            seg_text_lower = seg_text.lower()
            
            # Determine segment role tag
            role_tag = "General"
            if re.search(r"(cybersecurity|simulation|fictional|awareness training|memo ends|the right response|never share|no payment required|official published)", seg_text_lower):
                role_tag = "Educational Note"
            elif re.search(r"(won't share|will not share|won't give|will not provide|refuse)", seg_text_lower):
                role_tag = "Victim Refusal"
            elif re.search(r"(tell me the|please tell me|share the otp|one time password|please provide the otp|suspicious transaction|verify your identity|calling from the bank|arrest warrant|customs)", seg_text_lower):
                if not re.search(r"(do not need|never share|no payment|not asking)", seg_text_lower):
                    role_tag = "Attacker Request"

            seg_matched_phrases = []
            is_high = False
            for match in matches:
                key_words = [w for w in re.split(r'\W+', match.matched_phrase.lower()) if len(w) > 4]
                if any(w in seg_text_lower for w in key_words) or match.matched_phrase.lower() in seg_text_lower:
                    is_high = True
                    seg_matched_phrases.append(match.category)
            
            if role_tag == "Attacker Request":
                is_high = True

            updated_segments.append(TranscriptSegment(
                start_time=start_t,
                end_time=end_t,
                text=seg_text,
                is_scam_highlighted=is_high,
                matched_phrases=list(set(seg_matched_phrases)),
                role_tag=role_tag
            ))

        return TranscriptAnalysisResult(
            full_transcript=transcript,
            script_risk_score=round(float(script_risk_score), 1),
            detected_categories=detected_categories,
            matches=matches,
            segments=updated_segments,
            social_engineering=social_engineering
        )

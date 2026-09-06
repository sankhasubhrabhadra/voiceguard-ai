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

# Curated Seed Dataset of Scam Phrases across high-risk vector categories (English + Hindi + Hinglish)
SCAM_SEED_DATABASE = [
    # 1. Digital Arrest & Law Enforcement / Customs Impersonation
    {
        "category": "Digital Arrest & Law Enforcement Impersonation",
        "severity": 1.0,
        "description": "Impersonating police, CBI, Customs or judiciary to intimidate victim with false legal charges.",
        "phrases": [
            # English
            "This is officer from Delhi Police Crime Branch calling regarding money laundering",
            "A FedEx parcel containing illegal contraband and narcotics has been seized in your name at Mumbai customs",
            "You are currently placed under digital arrest and must stay on this video call",
            "An arrest warrant has been issued by the Supreme Court for illicit financial transactions",
            "Your Aadhaar number is implicated in 16 bank accounts used for human trafficking",
            "Do not hang up this call, our officers are tracking your GPS location",
            "This is Narcotics Control Bureau NCB regarding an intercepted international shipment",
            "Customs clearance officer has confiscated a package with duplicate passports in your name",
            # Hindi (Devanagari)
            "यह दिल्ली पुलिस क्राइम ब्रांच से बोल रहा हूँ, आपके नाम पर मनी लॉन्ड्रिंग और गैर-कानूनी गतिविधि का केस दर्ज हुआ है",
            "मुंबई कस्टम्स में आपके नाम का फेडेक्स पार्सल जब्त हुआ है जिसमें ड्रग्स और नशीले पदार्थ मिले हैं",
            "आपको तुरंत डिजिटल अरेस्ट में रखा गया है, यह वीडियो कॉल डिस्कनेक्ट मत करना नहीं तो पुलिस घर आ जाएगी",
            "सुप्रीम कोर्ट से आपके खिलाफ गैर-जमानती अरेस्ट वारंट जारी हुआ है",
            "नारकोटिक्स कंट्रोल ब्यूरो एनसीबी से बोल रहा हूँ, आपके आधार कार्ड का गलत इस्तेमाल हुआ है",
            "कस्टम अधिकारी ने आपके नाम का पार्सल रोका है, तुरंत अपने दस्तावेज और पहचान सत्यापित करें",
            # Hinglish (Roman Script)
            "Aapke naam pe Mumbai customs mein illegal FedEx narcotics parcel pakda gaya hai",
            "Yeh Delhi Crime Branch police station se bol raha hu, aap par digital arrest lag gaya hai",
            "Call mat kaatna nahi toh local police station se patrol gaadi aapke address par bhej rahe hain",
            "Supreme court se arrest warrant issue hua hai money laundering investigation ke liye",
            "NCB office se baat kar raha hu, aapke aadhar card par fake bank account khula hai"
        ]
    },
    # 2. OTP & Financial Credential Theft
    {
        "category": "OTP & Banking Credential Theft",
        "severity": 0.95,
        "description": "Attempting to harvest one-time passwords, CVV, or banking credentials under false pretenses.",
        "phrases": [
            # English
            "Your bank account and debit card will be suspended within two hours due to KYC expiry",
            "Please tell me the six digit OTP verification code sent to your phone to update your KYC",
            "We are calling from the fraud prevention division to reverse an unauthorized transaction",
            "Read out the SMS verification code received on your registered mobile number",
            "Provide your CVV number and ATM PIN to reactivate your online net banking",
            "To stop the pending charge of 50,000 rupees, share the one time password immediately",
            "Your credit limit is being increased, verify the confirmation code on your screen",
            "We detected a suspicious transaction on your account, please tell me the one time password",
            "Please provide the OTP sent to your phone so I can cancel the suspicious transaction",
            # Hindi (Devanagari)
            "आपका बैंक खाता और एटीएम कार्ड आज ब्लॉक हो जाएगा क्योंकि केवाईसी की मियाद खत्म हो गई है",
            "अनाधिकृत लेनदेन रोकने और खाता अनब्लॉक करने के लिए तुरंत 6 अंकों का ओटीपी बताएं",
            "हम बैंक के फ्रॉड प्रिवेंशन विभाग से बोल रहे हैं, अपने फोन पर आया वेरिफिकेशन कोड बताइए",
            "अपना एटीएम पिन और सीवीवी नंबर बताइए ताकि आपका खाता तुरंत चालू किया जा सके",
            "संदिग्ध ट्रांजेक्शन को कैंसिल करने के लिए मोबाइल पर भेजा गया ओटीपी तुरंत बताएं",
            # Hinglish (Roman Script)
            "Aapka bank account aur debit card block hone wala hai, turant 6 digit OTP share kijiye",
            "Main SBI fraud division se bol raha hu, pending transaction cancel karne ke liye OTP batayein",
            "KYC verification update karne ke liye phone par aaya hua SMS code read out kijiye",
            "ATM PIN aur CVV number verify karwayein taaki account active rahe"
        ]
    },
    # 3. Urgency & Coercive Intimidation
    {
        "category": "Urgent Coercion & Escrow Demands",
        "severity": 0.90,
        "description": "Creating panic and demanding immediate fund transfer to fraudulent 'safe verification accounts'.",
        "phrases": [
            # English
            "Transfer your entire bank balance to the government RBI secret security escrow account for clearance",
            "Do not inform any family members or lawyer as this is a classified national security investigation",
            "If you disconnect this call, a police patrol vehicle will arrive at your home address immediately",
            "You have exactly 30 minutes to make the security deposit or all your family bank accounts will be frozen",
            "Pay the penalty fine immediately via UPI to cancel the pending non-bailable arrest warrant",
            # Hindi (Devanagari)
            "आरबीआई के सरकारी सुरक्षित एस्क्रो खाते में अपने सारे पैसे तुरंत ट्रांसफर करें जांच पूरी होने तक",
            "किसी वकील या परिवार वाले को मत बताना यह गोपनीय राष्ट्रीय सुरक्षा जांच का मामला है",
            "अगर आपने कॉल काटा तो पुलिस पेट्रोलिंग गाड़ी तुरंत आपके घर भेज दी जाएगी",
            "30 मिनट के अंदर पैसे ट्रांसफर नहीं किए तो आपकी सारी संपत्ति और खाते सीज कर दिए जाएंगे",
            "गिरफ्तारी से बचने के लिए तुरंत यूपीआई से पेनल्टी जुर्माना भरें",
            # Hinglish (Roman Script)
            "RBI ke secret government security escrow account mein saara balance transfer karo verification ke liye",
            "Kisi ko mat batana yeh confidential investigation hai, call disconnect kiya toh arrest ho jaoge",
            "Turant UPI se penalty charge pay kijiye taaki non bailable warrant cancel ho sake"
        ]
    },
    # 4. Remote Access & Device Compromise
    {
        "category": "Remote Access Device Hijack",
        "severity": 0.85,
        "description": "Instructing the victim to install remote desktop software (AnyDesk, TeamViewer) to steal funds.",
        "phrases": [
            # English
            "Install AnyDesk or TeamViewer on your mobile device so our technical officer can assist you",
            "Download QuickSupport app from Google Play Store and give me the nine digit connection ID",
            "Open screen sharing application and accept the incoming remote connection request",
            "Download this bank security APK utility file sent on WhatsApp to fix the software error",
            # Hindi (Devanagari)
            "अपने मोबाइल में तुरंत AnyDesk या TeamViewer ऐप डाउनलोड करें ताकि हमारी टेक्निकल टीम मदद कर सके",
            "प्ले स्टोर से QuickSupport ऐप इंस्टॉल करें और 9 अंकों का कनेक्शन आईडी हमें दें",
            "स्क्रीन शेयरिंग शुरू करें और आने वाली रिमोट रिक्वेस्ट को एक्सेप्ट करें",
            "व्हाट्सएप पर भेजी गई बैंक सुरक्षा APK फाइल डाउनलोड और इंस्टॉल करें",
            # Hinglish (Roman Script)
            "Apne phone mein AnyDesk ya QuickSupport app install karo aur connection code share karo",
            "Screen share option on karke remote access allow kijiye technical support ke liye",
            "WhatsApp par bheja hua bank security APK file install kijiye"
        ]
    }
]

class ScamDetector:
    """
    Multilingual Semantic and Behavioral Scam Detection Engine (English + Hindi + Hinglish).
    Uses Sentence-Transformers embeddings combined with contextual multi-lingual pattern heuristics.
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

    def detect_language(self, transcript: str) -> str:
        """Determines whether transcript is Hindi (Devanagari), Hinglish, or English."""
        if bool(re.search(r'[\u0900-\u097F]', transcript)):
            return "Hindi (हिंदी)"
        
        # Check for Hinglish phonetics
        hinglish_keywords = [
            r"\b(bol raha|karo|nahi|batayein|kijiye|aapka|aapke|mera|meri|hoga|hogi|gaya|gayi|khata|paise|bhejo|kaatna)\b"
        ]
        for hk in hinglish_keywords:
            if re.search(hk, transcript, re.IGNORECASE):
                return "Hindi (Hinglish)"
                
        return "English"

    def analyze_transcript(self, transcript: str, segments: List[TranscriptSegment], stt_lang: Optional[str] = None) -> TranscriptAnalysisResult:
        """
        Analyzes the full transcript and segments for scam phrases, social engineering indicators,
        and role intent across English, Hindi, and Hinglish.
        """
        detected_lang = self.detect_language(transcript) if not stt_lang else (
            "Hindi (हिंदी)" if stt_lang == "hi" else self.detect_language(transcript)
        )

        if not transcript or len(transcript.strip()) < 4:
            return TranscriptAnalysisResult(
                full_transcript=transcript or "",
                detected_language=detected_lang,
                script_risk_score=0.0,
                detected_categories=[],
                matches=[],
                segments=segments,
                social_engineering=SocialEngineeringDetails()
            )

        # Ensure seed embeddings are loaded
        _ = self.model

        # Split transcript into candidate sentences / clauses
        sentences = [s.strip() for s in re.split(r'[.!?\n।]+', transcript) if len(s.strip()) > 6]
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
                r"(do not need|never share|never ask|no payment|not asking|will never ask|won't ask|should never share|caution|memo ends|the right response|mat share karna|nahi mangti|नहीं मांगते|मत बताना)",
                s_lower
            ))
            if is_negative_disclaimer:
                continue

            sims = sim_matrix[s_idx]
            top_seed_indices = np.where(sims >= 0.50)[0]
            
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

        # Lexical keyword & regex triggers across fraud domains (English + Hindi + Hinglish)
        lexical_triggers = [
            # Digital Arrest / Law Enforcement
            (r"(digital arrest|digitally arrested|डिजिटल अरेस्ट|डिजिटली अरेस्ट)", "Digital Arrest & Law Enforcement Impersonation", 0.98, "Explicit mention of illegal 'digital arrest' coercion."),
            (r"(delhi police|mumbai police|crime branch|narcotics control bureau|ncb|customs department|cbi|दिल्ली पुलिस|मुंबई पुलिस|क्राइम ब्रांच|कस्टम विभाग|कस्टम्स|सीबीआई|नारकोटिक्स|कस्टम अधिकारी|वारंट|warrant|गिरफ्तार)", "Digital Arrest & Law Enforcement Impersonation", 0.88, "Law enforcement / Customs authority impersonation."),
            
            # Banking / OTP Credential Theft
            (r"(bank('?s)? fraud prevention|card security division|fraud division|फ्रॉड प्रिवेंशन|बैंक मैनेजर|बैंक अधिकारी)", "OTP & Banking Credential Theft", 0.88, "Bank fraud department impersonation."),
            (r"(tell me (the|your)?\s*(\w+\s*){0,3}(one time password|otp|verification code|pin|password)|share (the|your)?\s*(\w+\s*){0,3}(otp|code|pin)|provide (the|your)?\s*(\w+\s*){0,3}(cvv|pin|otp|one time password)|ओटीपी बताएं|ओटीपी दीजिए|ओटीपी शेयर|वेरिफिकेशन कोड बताएं|पिन बताएं|सीवीवी बताएं|otp batayein|otp share karein|code dijiye)", "OTP & Banking Credential Theft", 0.96, "Direct solicitation of secure verification codes/OTP."),
            (r"(suspicious transaction|unauthorized transaction|account (will be |is )?blocked|card suspended|urgent verification|to cancel it|खाता ब्लॉक|कार्ड ब्लॉक|केवाईसी एक्सपायर|kyc expiry|अनाधिकृत लेनदेन)", "OTP & Banking Credential Theft", 0.84, "Fabricated financial alarm and account urgency."),
            
            # Remote Desktop Control
            (r"(anydesk|teamviewer|quicksupport|rustdesk|screen share|एनीडेस्क|टीमव्यूअर|क्विकसपोर्ट|स्क्रीन शेयर|apk फाइल|apk download)", "Remote Access Device Hijack", 0.92, "Instruction to install remote control software / APK."),
            
            # Escrow / Fund Demands
            (r"(rbi safe account|security escrow|secret account|transfer balance|आरबीआई सुरक्षित खाता|सरकारी एस्क्रो खाता|पैसे ट्रांसफर|जुर्माना भरें|penalty fine)", "Urgent Coercion & Escrow Demands", 0.95, "Demand for immediate escrow fund transfer.")
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
                if re.search(r"(do not need|never share|never ask|no payment|not asking|will never ask|मत बताना|शेयर मत करना)", context_lower):
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

        # --- Contextual Intent & Behavioral Analysis (Multilingual) ---
        # 1. Sensitive Information Request
        has_affirmative_sensitive = bool(re.search(
            r"(tell me (the|your)?\s*(\w+\s*){0,3}(one time password|otp|pin|password|code|cvv)|share (the|your)?\s*(\w+\s*){0,3}(otp|code|pin)|provide (your|the)?\s*(\w+\s*){0,3}(pin|cvv|otp|code|one time password)|give me (the|your)?\s*(\w+\s*){0,3}(otp|code)|read out the\s*(\w+\s*){0,3}(otp|code)|ओटीपी बताएं|ओटीपी दीजिए|ओटीपी शेयर|कोड बताइए|पिन बताइए|otp batayein|otp share karein|code dijiye)",
            transcript_lower
        ))
        has_negative_sensitive = bool(re.search(
            r"(do not need any (password|pin|otp|card)|never share (an|your|any)? (otp|password|pin|code)|will never ask for (your|any)? (password|pin|otp|card)|ओटीपी कभी शेयर न करें|बैंक कभी ओटीपी नहीं मांगता|kisi se otp share mat karein)",
            transcript_lower
        ))
        
        has_sensitive_req = has_affirmative_sensitive and not (has_negative_sensitive and not bool(re.search(r"(please tell me|please provide|कृपया बताएं|तुरंत बताएं)", transcript_lower)))

        # 2. Urgency
        has_urgency = bool(re.search(
            r"(immediate|urgently|within \d+ (minutes|hours)|to cancel it|suspicious transaction|account (will be |is )?blocked|card suspended|do not hang up|right now|तुरंत|जल्दी|30 मिनट|कॉल मत काटना|कॉल डिस्कनेक्ट मत करना|turant|call mat kaatna)",
            transcript_lower
        )) and not bool(re.search(r"(review is still in progress|no payment required)", transcript_lower))

        # 3. Authority Impersonation
        has_impersonation = bool(re.search(
            r"(fraud prevention team|delhi police|mumbai police|crime branch|customs|cbi|narcotics|police officer|authorized officer|पुलिस|क्राइम ब्रांच|कस्टम अधिकारी|सीबीआई|बैंक अधिकारी|ncb officer)",
            transcript_lower
        ))

        # 4. Financial Fraud Tactic
        has_financial_fraud = bool(re.search(
            r"(suspicious transaction|unauthorized charge|cancel (the|it|transaction)|kyc expiry|security escrow|transfer balance|penalty fine|पैसे ट्रांसफर|खाता ब्लॉक|एस्क्रो खाता|जुर्माना|transferred|balance transfer)",
            transcript_lower
        )) and not bool(re.search(r"(no payment required)", transcript_lower))

        # 5. Victim Defensive Refusal
        has_defensive_refusal = bool(re.search(
            r"(i won't share|i will not (share|give|provide)|not sharing|i refuse|won't give|will not share|won't provide|i will call the bank|i'm hanging up|मैं ओटीपी नहीं दूंगा|ओटीपी नहीं बताऊंगा|ओटीपी शेयर नहीं करूंगा|कॉल काट रहा हूँ|main otp nahi dunga|nahi share karunga)",
            transcript_lower
        ))

        # 6. Educational / Security Awareness Context
        has_educational_context = bool(re.search(
            r"(cybersecurity|simulation|fictional fraud call|fictional call|awareness training|memo ends|the right response|never share (an|your)? otp|educational purposes|training demonstration|simulated call|test simulation|जागरूकता|ट्रेनिंग डेमो)",
            transcript_lower
        ))

        # 7. General Social Engineering Flag
        has_social_eng = has_sensitive_req or has_impersonation or has_financial_fraud or has_urgency

        is_simulation = has_educational_context and (has_sensitive_req or has_impersonation or has_financial_fraud)

        # Flagged intents and evidence
        flagged_intents = []
        evidence_list = []

        if has_sensitive_req:
            flagged_intents.append("Direct OTP / Credential Harvesting Request (ओटीपी चोरी)")
            evidence_list.append("Caller requested confidential credentials (OTP/PIN/Password) in Hindi or English.")
        if has_impersonation:
            flagged_intents.append("Law Enforcement / Bank Authority Impersonation (पुलिस/बैंक अधिकारी पहचान चोरी)")
            evidence_list.append("Caller claimed authority association (Police, CBI, Customs, Bank Fraud Team).")
        if has_financial_fraud:
            flagged_intents.append("Fabricated Suspicious Transaction & Financial Alarm (खाता ब्लॉक / फर्जी लेनदेन धमकी)")
            evidence_list.append("Caller asserted pending unauthorized transaction or account blockage.")
        if has_urgency:
            flagged_intents.append("Urgency & Coercive Pressure Tactics (जल्दबाजी और कानूनी दबाव)")
            evidence_list.append("Caller exerted strict time pressure or digital arrest intimidation.")
        if has_defensive_refusal:
            flagged_intents.append("Victim Defensive Resistance Recognized (पीड़ित द्वारा इनकार)")
            evidence_list.append("Callee appropriately refused to provide credentials over the phone.")
        if has_educational_context:
            flagged_intents.append("Cybersecurity Awareness / Simulation Context Detected")
            evidence_list.append("Speech includes explicit training, awareness, or simulation disclaimers.")

        # Compute Social Engineering Risk Subscore (0 to 100)
        se_points = 0.0
        if has_sensitive_req:
            se_points += 45.0
        if has_impersonation:
            se_points += 25.0
        if has_urgency:
            se_points += 20.0
        if has_financial_fraud:
            se_points += 15.0
        se_score = min(100.0, se_points)

        social_engineering = SocialEngineeringDetails(
            score=round(se_score, 1),
            scam_probability=round(min(99.0, se_score * 1.05), 1),
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

        # Highlight transcript segments
        flagged_categories = list(set([m.category for m in matches]))
        
        normalized_segments: List[TranscriptSegment] = []
        for raw_seg in segments:
            if isinstance(raw_seg, dict):
                seg = TranscriptSegment(
                    start_time=float(raw_seg.get("start_time", 0.0)),
                    end_time=float(raw_seg.get("end_time", 0.0)),
                    text=str(raw_seg.get("text", "")),
                    is_scam_highlighted=bool(raw_seg.get("is_scam_highlighted", False)),
                    matched_phrases=list(raw_seg.get("matched_phrases", [])),
                    role_tag=raw_seg.get("role_tag", "General")
                )
            else:
                seg = raw_seg

            seg_text = seg.text or ""
            seg_lower = seg_text.lower()
            seg_matches = []
            
            for m in matches:
                # Check snippet overlap
                words = [w for w in re.split(r'\W+', m.matched_phrase.lower()) if len(w) > 3]
                if any(w in seg_lower for w in words):
                    seg_matches.append(m.category)
            
            if seg_matches:
                seg.is_scam_highlighted = True
                seg.matched_phrases = list(set(seg_matches))
                
                # Assign role tag
                if re.search(r"(tell me|share|provide|give me|install|download|transfer|arrest|block|ओटीपी|बताएं|ट्रांसफर)", seg_lower):
                    seg.role_tag = "Attacker Request"
                elif re.search(r"(won't share|will not|refuse|hanging up|नहीं दूंगा|नहीं बताऊंगा)", seg_lower):
                    seg.role_tag = "Victim Refusal"
                elif re.search(r"(cybersecurity|awareness|training|memo)", seg_lower):
                    seg.role_tag = "Educational Note"
                else:
                    seg.role_tag = "Suspicious Intent"
            
            normalized_segments.append(seg)

        # Calculate final script risk score (0-100)
        if not matches and not has_social_eng:
            script_risk_score = 4.0
        else:
            weighted_scores = [m.similarity_score * m.severity_weight for m in matches]
            max_semantic_risk = max(weighted_scores) if weighted_scores else 0.0
            
            # Combine semantic similarity with behavioral points
            combined_risk = max(max_semantic_risk, se_score)
            
            if has_sensitive_req and has_impersonation:
                combined_risk = max(combined_risk, 92.0)
            elif any(m.category == "Digital Arrest & Law Enforcement Impersonation" for m in matches):
                combined_risk = max(combined_risk, 90.0)
            elif has_sensitive_req:
                combined_risk = max(combined_risk, 82.0)
                
            script_risk_score = min(99.0, max(0.0, combined_risk))

        return TranscriptAnalysisResult(
            full_transcript=transcript,
            detected_language=detected_lang,
            script_risk_score=round(script_risk_score, 1),
            detected_categories=flagged_categories,
            matches=matches,
            segments=normalized_segments,
            social_engineering=social_engineering
        )

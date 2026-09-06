import os
import json
import logging
import requests
from typing import Optional, Dict, Any, List, Tuple
from app.models import OllamaInsight

logger = logging.getLogger("voiceguard.ollama")

class OllamaAnalyzer:
    """
    Optional Local LLM integration via Ollama (http://localhost:11434).
    Provides deep cognitive forensics on call transcripts:
    - Psychological coercion & urgency manipulation detection
    - Authority impersonation classification
    - Sensitive credential harvesting vectors
    - Tactical defense advice
    """
    def __init__(self, base_url: Optional[str] = None, timeout_seconds: float = 4.0):
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.timeout = timeout_seconds
        self.preferred_models = ["llama3.2", "llama3.1", "llama3", "mistral", "gemma2", "qwen2.5", "phi3"]

    def get_active_model(self) -> Optional[str]:
        """Check if Ollama server is running and return the best available model name."""
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=0.5)
            if res.status_code == 200:
                data = res.json()
                models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
                full_names = [m.get("name", "") for m in data.get("models", [])]
                
                # Check preferred list
                for pref in self.preferred_models:
                    for full in full_names:
                        if full.startswith(pref):
                            return full
                
                # If any model exists, return the first one
                if full_names:
                    return full_names[0]
        except Exception as e:
            logger.debug(f"Ollama server not reachable at {self.base_url}: {e}")
        return None

    def analyze_transcript(self, transcript: str, voice_risk: float = 0.0) -> OllamaInsight:
        """
        Analyze the call transcript using local Ollama model.
        Returns OllamaInsight with threat breakdown and recommended defense.
        """
        model = self.get_active_model()
        if not model or not transcript or len(transcript.strip()) < 10:
            return OllamaInsight(enabled=False, model_name=model)

        prompt = f"""You are VoiceGuard AI, an elite cybersecurity and telecommunications fraud investigator specializing in multi-lingual voice scams across English, Hindi (हिंदी), and Hinglish.
Analyze this intercepted phone call transcript for social engineering tactics, authority impersonation (e.g. Police/CBI Digital Arrest, Bank OTP theft, Customs parcel extortion), and fraudulent intent.

TRANSCRIPT (May be in English, Hindi, or Hinglish):
\"\"\"{transcript}\"\"\"

Provide your analysis ONLY as a valid JSON object matching this exact schema:
{{
  "threat_summary": "1-2 concise sentences in clear English summarizing the scam vector, language context, and attacker strategy.",
  "psychological_tactics": ["Tactic 1 (e.g. Digital Arrest / Fake Police Coercion)", "Tactic 2 (e.g. OTP Harvesting / Urgency)"],
  "recommended_defense": "1-2 actionable safety instructions for the victim."
}}

Respond with valid JSON only. Do not include markdown code blocks or additional text."""

        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 300
                }
            }
            res = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=self.timeout)
            if res.status_code == 200:
                raw_response = res.json().get("response", "").strip()
                # Parse JSON
                # Clean possible markdown formatting
                if raw_response.startswith("```"):
                    raw_response = raw_response.split("```")[1]
                    if raw_response.startswith("json"):
                        raw_response = raw_response[4:]
                    raw_response = raw_response.strip()
                
                data = json.loads(raw_response)
                return OllamaInsight(
                    enabled=True,
                    model_name=model,
                    threat_summary=data.get("threat_summary"),
                    psychological_tactics=data.get("psychological_tactics", []),
                    recommended_defense=data.get("recommended_defense")
                )
        except Exception as e:
            logger.warning(f"Ollama generation failed or timed out: {e}")

        return OllamaInsight(enabled=False, model_name=model)

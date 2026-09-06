import os
import soundfile as sf
import numpy as np
import librosa
from typing import Dict, Any, List, Optional
import whisper
from app.models import TranscriptSegment

class STTEngine:
    """
    OpenAI Whisper Speech-to-Text Engine for local speech recognition.
    Uses in-memory 16kHz float32 audio buffers directly to avoid ffmpeg CLI subprocess dependencies.
    """
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None

    def warmup(self):
        """Preloads Whisper weights during server startup."""
        _ = self.model

    @property
    def model(self):
        if self._model is None:
            try:
                print(f"Loading Whisper model '{self.model_size}'...")
                self._model = whisper.load_model(self.model_size)
            except Exception as e:
                print(f"Warning: loading whisper model '{self.model_size}' failed ({e}). Falling back to 'tiny'.")
                self._model = whisper.load_model("tiny")
        return self._model

    def transcribe(self, audio_path: str, y: Optional[np.ndarray] = None, sr: int = 16000) -> Dict[str, Any]:
        """
        Transcribes audio into full text and timestamped segments.
        Accepts either direct numpy array y or audio_path.
        """
        try:
            # 1. Ensure we have 16kHz mono float32 numpy array
            if y is None or len(y) == 0:
                y, file_sr = sf.read(audio_path)
                if len(y.shape) > 1:
                    y = np.mean(y, axis=1)
                if file_sr != 16000:
                    y = librosa.resample(y, orig_sr=file_sr, target_sr=16000)

            audio_data = y.astype(np.float32)

            # 2. Transcribe directly with in-memory array
            result = self.model.transcribe(
                audio_data,
                fp16=False,
                language="en",
                verbose=False
            )

            full_text = result.get("text", "").strip()
            raw_segments = result.get("segments", [])
            
            segments: List[TranscriptSegment] = []
            for seg in raw_segments:
                seg_text = seg.get("text", "").strip()
                if seg_text:
                    segments.append(TranscriptSegment(
                        start_time=round(float(seg.get("start", 0.0)), 2),
                        end_time=round(float(seg.get("end", 0.0)), 2),
                        text=seg_text,
                        is_scam_highlighted=False,
                        matched_phrases=[]
                    ))

            if not segments and full_text:
                duration = float(len(audio_data) / 16000)
                segments.append(TranscriptSegment(
                    start_time=0.0,
                    end_time=round(duration, 2),
                    text=full_text,
                    is_scam_highlighted=False,
                    matched_phrases=[]
                ))

            return {
                "full_text": full_text,
                "segments": segments,
                "language": result.get("language", "en")
            }

        except Exception as e:
            print(f"Whisper transcription exception: {e}")
            import traceback
            traceback.print_exc()
            return {
                "full_text": "",
                "segments": [],
                "language": "en"
            }

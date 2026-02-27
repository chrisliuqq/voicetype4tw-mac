import httpx
import base64
import io
from .base import BaseSTT

class GeminiSTT(BaseSTT):
    """Google Gemini STT (Audio understanding)"""

    def __init__(self, config: dict):
        self.api_key = config.get("gemini_api_key", "")
        self.model = config.get("gemini_stt_model", "gemini-2.0-flash")
        self.language = config.get("language", "zh")

    def transcribe(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        if not self.api_key:
            return ""
        try:
            import soundfile as sf
            buf = io.BytesIO()
            sf.write(buf, audio_data, sample_rate, format="WAV")
            audio_b64 = base64.b64encode(buf.getvalue()).decode()

            lang_hint = "Traditional Chinese" if self.language == "zh" else "English"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{
                    "parts": [
                        {"text": f"Please transcribe this audio accurately in {lang_hint}. Return only the transcribed text, nothing else."},
                        {"inline_data": {"mime_type": "audio/wav", "data": audio_b64}}
                    ]
                }]
            }
            resp = httpx.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"[Gemini STT Error] {e}")
            return ""

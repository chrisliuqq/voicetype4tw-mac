import httpx
import io
from .base import BaseSTT

class OpenRouterSTT(BaseSTT):
    """OpenRouter STT — 使用 Whisper Large v3 (via OpenRouter)"""

    def __init__(self, config: dict):
        self.api_key = config.get("openrouter_api_key", "")
        self.language = config.get("language", "zh")

    def transcribe(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        if not self.api_key:
            return ""
        try:
            import soundfile as sf
            buf = io.BytesIO()
            sf.write(buf, audio_data, sample_rate, format="WAV")
            buf.seek(0)
            files = {"file": ("audio.wav", buf, "audio/wav")}
            data = {"model": "openai/whisper-large-v3", "language": self.language}
            headers = {"Authorization": f"Bearer {self.api_key}"}
            resp = httpx.post(
                "https://openrouter.ai/api/v1/audio/transcriptions",
                headers=headers,
                files=files,
                data=data,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json().get("text", "").strip()
        except Exception as e:
            print(f"[OpenRouter STT Error] {e}")
            return ""

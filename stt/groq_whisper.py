import io
from groq import Groq
from .base import BaseSTT


class GroqWhisperSTT(BaseSTT):
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def transcribe(self, audio_bytes: bytes, language: str = "zh") -> str:
        if not audio_bytes:
            return ""
        transcription = self.client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=("audio.wav", io.BytesIO(audio_bytes), "audio/wav"),
            language=language,
            response_format="text",
        )
        text = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
        print(f"[stt] Groq transcribed: {text}")
        return text

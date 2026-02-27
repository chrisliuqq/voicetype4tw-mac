from faster_whisper import WhisperModel
import io
import numpy as np
import wave
from .base import BaseSTT


class LocalWhisperSTT(BaseSTT):
    def __init__(self, model_size: str = "medium"):
        print(f"[stt] Loading local Whisper model: {model_size} ...")
        self.model = WhisperModel(model_size, device="auto", compute_type="int8")
        print("[stt] Model loaded.")

    def transcribe(self, audio_bytes: bytes, language: str = "zh") -> str:
        if not audio_bytes:
            return ""
        # 動態從詞彙庫組合 initial_prompt
        try:
            from vocab.manager import build_vocab_prompt
            prompt = build_vocab_prompt()
        except Exception:
            prompt = "以下是繁體中文的語音內容："

        audio_io = io.BytesIO(audio_bytes)
        segments, info = self.model.transcribe(
            audio_io,
            language=language,
            beam_size=1,
            vad_filter=True,
            initial_prompt=prompt,
        )
        text = "".join(seg.text for seg in segments).strip()
        print(f"[stt] Transcribed ({info.language}): {text}")
        return text

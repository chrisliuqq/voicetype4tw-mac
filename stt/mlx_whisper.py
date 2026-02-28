import io
import wave
import numpy as np
from .base import BaseSTT

MODEL_REPO_MAP = {
    "tiny":   "mlx-community/whisper-tiny-mlx",
    "base":   "mlx-community/whisper-base-mlx",
    "small":  "mlx-community/whisper-small-mlx",
    "medium": "mlx-community/whisper-medium-mlx",
    "large":  "mlx-community/whisper-large-v3-mlx",
}


class MLXWhisperSTT(BaseSTT):
    def __init__(self, model_size: str = "medium"):
        self.model_repo = MODEL_REPO_MAP.get(model_size, MODEL_REPO_MAP["medium"])
        print(f"[stt] MLX Whisper model: {self.model_repo} (lazy load on first use)")

    def transcribe(self, audio_bytes: bytes, language: str = "zh") -> str:
        if not audio_bytes:
            return ""

        try:
            from vocab.manager import build_vocab_prompt
            prompt = build_vocab_prompt()
        except Exception:
            prompt = "以下是繁體中文的語音內容："

        # WAV bytes → float32 numpy array [-1, 1]
        audio_io = io.BytesIO(audio_bytes)
        with wave.open(audio_io, "rb") as wf:
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            n_frames = wf.getnframes()
            raw_data = wf.readframes(n_frames)

        if sampwidth == 2:
            audio_np = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
        else:
            audio_np = np.frombuffer(raw_data, dtype=np.float32)

        if n_channels > 1:
            audio_np = audio_np.reshape(-1, n_channels).mean(axis=1)

        import mlx_whisper
        result = mlx_whisper.transcribe(
            audio_np,
            path_or_hf_repo=self.model_repo,
            language=language,
            initial_prompt=prompt,
            verbose=False,
        )
        text = result.get("text", "").strip()
        print(f"[stt] MLX Whisper transcribed: {text}")
        return text

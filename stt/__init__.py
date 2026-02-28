from .base import BaseSTT
from .local_whisper import LocalWhisperSTT
from .groq_whisper import GroqWhisperSTT
from .openrouter_stt import OpenRouterSTT
from .gemini_stt import GeminiSTT
from .mlx_whisper import MLXWhisperSTT

def get_stt(config: dict) -> BaseSTT:
    engine = config.get("stt_engine", "local_whisper")
    engines = {
        "local_whisper": LocalWhisperSTT,
        "mlx_whisper": MLXWhisperSTT,
        "groq": GroqWhisperSTT,
        "openrouter": OpenRouterSTT,
        "gemini": GeminiSTT,
    }
    cls = engines.get(engine, LocalWhisperSTT)
    return cls(config)

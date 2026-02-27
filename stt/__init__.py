from .base import BaseSTT
from .local_whisper import LocalWhisperSTT
from .groq_whisper import GroqWhisperSTT
from .openrouter_stt import OpenRouterSTT
from .gemini_stt import GeminiSTT

def get_stt(config: dict) -> BaseSTT:
    engine = config.get("stt_engine", "local_whisper")
    engines = {
        "local_whisper": LocalWhisperSTT,
        "groq": GroqWhisperSTT,
        "openrouter": OpenRouterSTT,
        "gemini": GeminiSTT,
    }
    cls = engines.get(engine, LocalWhisperSTT)
    return cls(config)

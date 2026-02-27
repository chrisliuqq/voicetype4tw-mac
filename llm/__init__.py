from .base import BaseLLM
from .ollama import OllamaLLM
from .openai_llm import OpenAILLM
from .claude import ClaudeLLM
from .openrouter import OpenRouterLLM
from .gemini import GeminiLLM
from .qwen import QwenLLM
from .deepseek import DeepSeekLLM

def get_llm(config: dict) -> BaseLLM:
    engine = config.get("llm_engine", "ollama")
    engines = {
        "ollama": OllamaLLM,
        "openai": OpenAILLM,
        "claude": ClaudeLLM,
        "openrouter": OpenRouterLLM,
        "gemini": GeminiLLM,
        "qwen": QwenLLM,
        "deepseek": DeepSeekLLM,
    }
    cls = engines.get(engine, OllamaLLM)
    return cls(config)

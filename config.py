import json
import os

DEFAULT_CONFIG = {
    "hotkey_ptt": "alt_r",
    "hotkey_toggle": "f13",
    "hotkey_llm": "f14",
    # STT
    "stt_engine": "local_whisper",
    "whisper_model": "medium",
    "groq_api_key": "",
    "language": "zh",
    # LLM
    "llm_enabled": False,
    "llm_engine": "ollama",
    "llm_mode": "replace",   # "replace" | "fast"
    "llm_prompt": "",        # 留空使用內建 prompt
    "ollama_model": "llama3",
    "ollama_base_url": "http://localhost:11434",
    "openai_api_key": "",
    "openai_model": "gpt-4o-mini",
    "anthropic_api_key": "",
    "anthropic_model": "claude-3-haiku-20240307",
    "openrouter_api_key": "",
    "openrouter_model": "google/gemini-2.0-flash-001",
    "gemini_api_key": "",
    "gemini_model": "gemini-2.0-flash",
    "gemini_stt_model": "gemini-2.0-flash",
    "qwen_api_key": "",
    "qwen_model": "qwen-plus",
    "deepseek_api_key": "",
    "deepseek_model": "deepseek-chat",
    # 記憶
    "memory_enabled": True,
    # 統計 / Debug
    "debug_mode": False,
    # 其他
    "auto_paste": True,
}

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load_config() -> dict:
    """Load config from config.json, falling back to defaults for missing keys."""
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            config.update(user_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[config] Warning: failed to load config.json: {e}")
    return config


def save_config(config: dict) -> None:
    """Save config dict back to config.json."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

import httpx
from .base import BaseLLM

class OpenRouterLLM(BaseLLM):
    """OpenRouter LLM — 支援數百個模型 (Gemini, Qwen, DeepSeek...)"""

    def __init__(self, config: dict):
        self.api_key = config.get("openrouter_api_key", "")
        self.model = config.get("openrouter_model", "google/gemini-2.0-flash-001")
        self.prompt = config.get("llm_prompt", "請將以下語音辨識結果整理成通順的文字，保持原意，只回傳結果：")

    def refine(self, text: str, prompt: str) -> str:
        if not self.api_key:
            return text
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/voicetype-mac",
            "X-Title": "VoiceType Mac",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
        }
        try:
            resp = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[OpenRouter LLM Error] {e}")
            return text

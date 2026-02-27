import httpx
from .base import BaseLLM

class GeminiLLM(BaseLLM):
    """Google Gemini LLM"""

    def __init__(self, config: dict):
        self.api_key = config.get("gemini_api_key", "")
        self.model = config.get("gemini_model", "gemini-2.0-flash")
        self.prompt = config.get("llm_prompt", "請將以下語音辨識結果整理成通順的文字，保持原意，只回傳結果：")

    def refine(self, text: str, prompt: str) -> str:
        if not self.api_key:
            return text
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": f"{prompt}\n\n{text}"}]}]
        }
        try:
            resp = httpx.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"[Gemini LLM Error] {e}")
            return text

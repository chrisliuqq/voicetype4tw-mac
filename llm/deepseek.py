import httpx
from .base import BaseLLM

class DeepSeekLLM(BaseLLM):
    """DeepSeek LLM"""

    def __init__(self, config: dict):
        self.api_key = config.get("deepseek_api_key", "")
        self.model = config.get("deepseek_model", "deepseek-chat")
        self.prompt = config.get("llm_prompt", "請將以下語音辨識結果整理成通順的文字，保持原意，只回傳結果：")

    def refine(self, text: str, prompt: str) -> str:
        if not self.api_key:
            return text
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": f"{prompt}\n\n{text}"}
            ],
        }
        try:
            resp = httpx.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[DeepSeek LLM Error] {e}")
            return text

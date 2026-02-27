import httpx
from .base import BaseLLM

class QwenLLM(BaseLLM):
    """Alibaba Qwen LLM (DashScope API)"""

    def __init__(self, config: dict):
        self.api_key = config.get("qwen_api_key", "")
        self.model = config.get("qwen_model", "qwen-plus")
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
            "input": {
                "messages": [
                    {"role": "user", "content": f"{prompt}\n\n{text}"}
                ]
            },
        }
        try:
            resp = httpx.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                headers=headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["output"]["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[Qwen LLM Error] {e}")
            return text

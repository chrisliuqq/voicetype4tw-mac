import requests
from .base import BaseLLM


class OllamaLLM(BaseLLM):
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def refine(self, text: str, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            "stream": False,
        }
        resp = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()["message"]["content"].strip()
        print(f"[llm] Ollama refined: {result}")
        return result

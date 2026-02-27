import anthropic
from .base import BaseLLM


class ClaudeLLM(BaseLLM):
    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def refine(self, text: str, prompt: str) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=prompt,
            messages=[{"role": "user", "content": text}],
        )
        result = message.content[0].text.strip()
        print(f"[llm] Claude refined: {result}")
        return result

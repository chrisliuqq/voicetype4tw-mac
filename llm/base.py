from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    def refine(self, text: str, prompt: str) -> str:
        """Refine raw transcription text using the given system prompt."""
        ...

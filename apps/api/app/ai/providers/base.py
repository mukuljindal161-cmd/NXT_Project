from abc import ABC, abstractmethod
from typing import List, Generator, Optional


class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate a complete text response from LLM."""
        pass

    @abstractmethod
    def generate_stream(self, prompt: str, system_instruction: Optional[str] = None) -> Generator[str, None, None]:
        """Stream chunks of text from LLM."""
        pass

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Generate embedding vector for a single text."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for multiple texts in batch."""
        pass

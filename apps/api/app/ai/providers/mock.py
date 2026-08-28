import hashlib
import math
import re
from typing import List, Generator, Optional
from app.ai.providers.base import AIProvider
from app.config import settings


class MockAIProvider(AIProvider):
    def __init__(self, dimensions: int = 768):
        self.dimensions = dimensions

    def _hash_to_vector(self, text: str) -> List[float]:
        """Generate a deterministic normalized vector based on tokens and characters in text."""
        vec = [0.0] * self.dimensions
        clean_words = re.findall(r'\w+', text.lower())
        if not clean_words:
            clean_words = ["empty"]

        for word in clean_words:
            # Map word hash into dimension bins
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimensions
            val = ((h >> 8) % 1000) / 500.0 - 1.0  # -1.0 to 1.0
            vec[idx] += val

        # Normalize vector
        magnitude = math.sqrt(sum(v * v for v in vec))
        if magnitude == 0:
            vec[0] = 1.0
            magnitude = 1.0
        return [v / magnitude for v in vec]

    def embed(self, text: str) -> List[float]:
        return self._hash_to_vector(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(t) for t in texts]

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        # Extract question and context from prompt if possible
        if "Context:" in prompt:
            context_part = prompt.split("Context:")[1].split("Question:")[0].strip()
            # If context is empty or indicates no information
            if not context_part or len(context_part) < 10:
                return "I couldn't find enough information about that in the college knowledge base. Please try rephrasing your question or contact the relevant college office."
            
            return f"Based on the official college documents provided:\n\n{context_part[:400]}..."
        return "I am the College RAG Assistant. How can I help you with admissions, courses, fees, or campus policies today?"

    def generate_stream(self, prompt: str, system_instruction: Optional[str] = None) -> Generator[str, None, None]:
        full_text = self.generate(prompt, system_instruction)
        words = full_text.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")

import logging
from typing import List, Generator, Optional
from app.ai.providers.base import AIProvider
from app.ai.providers.mock import MockAIProvider
from app.config import settings

logger = logging.getLogger(__name__)


class GeminiAIProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.mock_fallback = MockAIProvider(dimensions=settings.EMBEDDING_DIMENSIONS)
        self._is_initialized = False

        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.genai = genai
                self.model_candidates = [
                    settings.LLM_MODEL or "gemini-3.6-flash",
                    "gemini-3.6-flash",
                    "gemini-flash-latest",
                    "gemini-2.5-flash",
                    "gemini-1.5-flash"
                ]
                self.embedding_candidates = [
                    settings.EMBEDDING_MODEL or "gemini-embedding-001",
                    "gemini-embedding-001",
                    "gemini-embedding-2",
                    "text-embedding-004"
                ]
                self._is_initialized = True
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini API: {e}. Falling back to mock provider.")
                self._is_initialized = False

    def embed(self, text: str) -> List[float]:
        if not self._is_initialized:
            return self.mock_fallback.embed(text)

        for emb_model in self.embedding_candidates:
            try:
                model_path = emb_model if emb_model.startswith("models/") else f"models/{emb_model}"
                result = self.genai.embed_content(
                    model=model_path,
                    content=text,
                    task_type="retrieval_query"
                )
                embedding = result["embedding"]
                return embedding
            except Exception as e:
                logger.debug(f"Gemini embed error with {emb_model}: {e}")
                continue

        logger.warning("All Gemini embedding models failed. Falling back to mock embedding.")
        return self.mock_fallback.embed(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not self._is_initialized:
            return self.mock_fallback.embed_batch(texts)

        for emb_model in self.embedding_candidates:
            try:
                model_path = emb_model if emb_model.startswith("models/") else f"models/{emb_model}"
                result = self.genai.embed_content(
                    model=model_path,
                    content=texts,
                    task_type="retrieval_document"
                )
                embeddings = result.get("embedding", [])
                if embeddings:
                    return embeddings
            except Exception:
                continue

        return [self.embed(t) for t in texts]

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        if not self._is_initialized:
            return self.mock_fallback.generate(prompt, system_instruction)

        for model_name in self.model_candidates:
            try:
                clean_name = model_name.replace("models/", "")
                model = self.genai.GenerativeModel(
                    model_name=clean_name,
                    system_instruction=system_instruction
                )
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text
            except Exception as e:
                logger.debug(f"Gemini generate error with {model_name}: {e}")
                continue

        logger.warning("All Gemini models failed to generate content. Falling back to mock response.")
        return self.mock_fallback.generate(prompt, system_instruction)

    def generate_stream(self, prompt: str, system_instruction: Optional[str] = None) -> Generator[str, None, None]:
        if not self._is_initialized:
            for chunk in self.mock_fallback.generate_stream(prompt, system_instruction):
                yield chunk
            return

        for model_name in self.model_candidates:
            try:
                clean_name = model_name.replace("models/", "")
                model = self.genai.GenerativeModel(
                    model_name=clean_name,
                    system_instruction=system_instruction
                )
                response = model.generate_content(prompt, stream=True)
                has_yielded = False
                for chunk in response:
                    if chunk.text:
                        has_yielded = True
                        yield chunk.text
                if has_yielded:
                    return
            except Exception as e:
                logger.debug(f"Gemini stream error with {model_name}: {e}")
                continue

        # Fallback to mock stream if generation fails
        for chunk in self.mock_fallback.generate_stream(prompt, system_instruction):
            yield chunk

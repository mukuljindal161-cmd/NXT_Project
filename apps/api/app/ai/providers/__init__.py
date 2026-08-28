from app.ai.providers.base import AIProvider
from app.ai.providers.gemini import GeminiAIProvider
from app.ai.providers.mock import MockAIProvider
from app.config import settings

_provider_instance = None


def get_ai_provider() -> AIProvider:
    global _provider_instance
    if _provider_instance is None:
        if settings.LLM_PROVIDER == "mock" or not settings.GEMINI_API_KEY:
            _provider_instance = MockAIProvider(dimensions=settings.EMBEDDING_DIMENSIONS)
        else:
            _provider_instance = GeminiAIProvider(api_key=settings.GEMINI_API_KEY)
    return _provider_instance

from app.config import settings
from app.ai.base import AIProvider
from app.ai.mock_provider import MockAIProvider
from app.ai.openai_provider import OpenAIProvider

_ai_instance: AIProvider = None

def get_ai_provider() -> AIProvider:
    """
    Factory function returning the singleton AIProvider.
    Defaults to MockAIProvider if AI_MOCK_MODE=True or if keys are missing.
    """
    global _ai_instance
    if _ai_instance is not None:
        return _ai_instance

    if settings.AI_MOCK_MODE or not settings.AI_API_KEY:
        _ai_instance = MockAIProvider()
    elif settings.AI_PROVIDER == "openai":
        _ai_instance = OpenAIProvider(api_key=settings.AI_API_KEY, model=settings.AI_MODEL)
    else:
        _ai_instance = MockAIProvider()

    return _ai_instance

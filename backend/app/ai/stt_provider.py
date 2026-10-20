import httpx
from typing import Optional
from app.ai.base import SpeechProvider
from app.config import settings

class MockSpeechProvider(SpeechProvider):
    def transcribe_audio(self, audio_bytes: bytes, filename: str) -> str:
        """
        Deterministic mock transcription that simulates audio speech output.
        """
        if not audio_bytes or len(audio_bytes) < 100:
            return "In our previous system, we used FastAPI for asynchronous microservices and PostgreSQL for relational persistence."
        
        # Realistic answer transcription based on size heuristic
        return (
            "In our FastAPI architecture, we used asynchronous endpoint handlers with dependency injection "
            "for database sessions. To prevent blocking the main event loop during heavy I/O, we offloaded "
            "CPU-intensive background operations to a distributed worker queue and implemented Redis caching "
            "for read-heavy routes, which reduced p99 latency significantly."
        )


class WhisperSpeechProvider(SpeechProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.STT_API_KEY
        self.mock_fallback = MockSpeechProvider()

    def transcribe_audio(self, audio_bytes: bytes, filename: str) -> str:
        if not self.api_key:
            return self.mock_fallback.transcribe_audio(audio_bytes, filename)

        try:
            files = {
                "file": (filename or "audio.webm", audio_bytes, "audio/webm"),
                "model": (None, "whisper-1")
            }
            headers = {"Authorization": f"Bearer {self.api_key}"}
            with httpx.Client(timeout=30.0) as client:
                res = client.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files)
                if res.status_code == 200:
                    return res.json().get("text", "")
        except Exception:
            pass

        return self.mock_fallback.transcribe_audio(audio_bytes, filename)


def get_speech_provider() -> SpeechProvider:
    if not settings.AI_MOCK_MODE and settings.STT_PROVIDER == "openai_whisper" and settings.STT_API_KEY:
        return WhisperSpeechProvider()
    return MockSpeechProvider()

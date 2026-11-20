from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from typing import Optional
from app.ai.stt_provider import get_speech_provider
from app.auth.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/voice", tags=["Voice & STT"])

ALLOWED_AUDIO_EXTENSIONS = {".webm", ".wav", ".mp4", ".ogg", ".m4a", ".mp3"}
MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25 MB

@router.post("/transcribe")
async def transcribe_audio_recording(
    audio: UploadFile = File(...),
    duration_seconds: Optional[float] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Transcribes an uploaded voice audio clip into text transcript."""
    filename = audio.filename or "recording.webm"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ".webm"
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format '{ext}'. Supported formats: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}"
        )

    try:
        audio_bytes = await audio.read()
        if not audio_bytes or len(audio_bytes) < 100:
            return {
                "transcript": "",
                "duration_seconds": duration_seconds or 0.0,
                "success": False,
                "message": "No audio data received or recording was empty."
            }

        if len(audio_bytes) > MAX_AUDIO_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audio file exceeds maximum size limit (25MB)."
            )

        provider = get_speech_provider()
        transcript = provider.transcribe_audio(audio_bytes, filename)

        return {
            "transcript": transcript.strip() if transcript else "",
            "duration_seconds": duration_seconds or 5.0,
            "success": bool(transcript and transcript.strip())
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio transcription service error: {str(e)}"
        )

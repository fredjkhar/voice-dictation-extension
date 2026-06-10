from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.security import normalize_content_type, safe_audio_filename, validate_audio_upload
from app.schemas.transcription import TranscriptionResponse
from app.services.xai_service import XAIConfigurationError, XAIServiceError, transcribe_audio as transcribe_with_xai

router = APIRouter(tags=["transcription"])


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio_route(file: UploadFile = File(...)) -> TranscriptionResponse:
    audio_bytes = await validate_audio_upload(file)

    try:
        result = await transcribe_with_xai(
            audio_bytes,
            filename=safe_audio_filename(file.filename),
            content_type=normalize_content_type(file.content_type) or "audio/webm",
        )
    except XAIConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Speech-to-text service is not configured.",
        ) from exc
    except XAIServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Speech-to-text service failed.",
        ) from exc

    return TranscriptionResponse(transcript=result.text)

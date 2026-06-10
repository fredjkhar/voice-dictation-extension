from pathlib import PurePath

from fastapi import HTTPException, UploadFile, status

MAX_AUDIO_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_AUDIO_FILENAME_LENGTH = 120
ALLOWED_AUDIO_CONTENT_TYPES = {
    "audio/mp4",
    "audio/mpeg",
    "audio/ogg",
    "audio/wav",
    "audio/webm",
    "audio/x-m4a",
}
ALLOWED_AUDIO_EXTENSIONS = {".m4a", ".mp3", ".mp4", ".ogg", ".wav", ".webm"}


def normalize_content_type(content_type: str | None) -> str:
    return (content_type or "").split(";", 1)[0].strip().lower()


def safe_audio_filename(filename: str | None) -> str:
    name = PurePath(filename or "recording.webm").name

    if not name or len(name) > MAX_AUDIO_FILENAME_LENGTH:
        return "recording.webm"

    suffix = PurePath(name).suffix.lower()
    if suffix not in ALLOWED_AUDIO_EXTENSIONS:
        return "recording.webm"

    return name


async def validate_audio_upload(file: UploadFile) -> bytes:
    content_type = normalize_content_type(file.content_type)

    if content_type not in ALLOWED_AUDIO_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported audio file type.",
        )

    contents = await file.read(MAX_AUDIO_UPLOAD_BYTES + 1)
    size = len(contents)

    if size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded audio file is empty.",
        )

    if size > MAX_AUDIO_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Uploaded audio file is too large.",
        )

    return contents

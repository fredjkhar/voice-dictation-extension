from fastapi.testclient import TestClient

from app.core.security import normalize_content_type, safe_audio_filename
from app.main import app
from app.routes import transcribe
from app.services.xai_service import XAIServiceError, XAITranscriptionResult


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_transcribe_returns_provider_transcript(monkeypatch) -> None:
    async def fake_transcribe(audio_bytes: bytes, *, filename: str, content_type: str) -> XAITranscriptionResult:
        assert audio_bytes == b"fake audio bytes"
        assert filename == "recording.webm"
        assert content_type == "audio/webm"
        return XAITranscriptionResult(text="Mock transcript.")

    monkeypatch.setattr(transcribe, "transcribe_with_xai", fake_transcribe)

    response = client.post(
        "/api/transcribe",
        files={"file": ("recording.webm", b"fake audio bytes", "audio/webm;codecs=opus")},
    )

    assert response.status_code == 200
    assert response.json() == {"transcript": "Mock transcript."}


def test_transcribe_rejects_wrong_file_type() -> None:
    response = client.post(
        "/api/transcribe",
        files={"file": ("note.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Unsupported audio file type."}


def test_transcribe_rejects_empty_audio() -> None:
    response = client.post(
        "/api/transcribe",
        files={"file": ("empty.webm", b"", "audio/webm")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Uploaded audio file is empty."}


def test_transcribe_returns_safe_provider_error(monkeypatch) -> None:
    async def fake_transcribe(_audio_bytes: bytes, *, filename: str, content_type: str) -> XAITranscriptionResult:
        raise XAIServiceError("upstream details should not reach the client")

    monkeypatch.setattr(transcribe, "transcribe_with_xai", fake_transcribe)

    response = client.post(
        "/api/transcribe",
        files={"file": ("recording.webm", b"fake audio bytes", "audio/webm")},
    )

    assert response.status_code == 502
    assert response.json() == {"detail": "Speech-to-text service failed."}


def test_content_type_and_filename_helpers() -> None:
    assert normalize_content_type("audio/webm;codecs=opus") == "audio/webm"
    assert normalize_content_type(" AUDIO/WAV ") == "audio/wav"
    assert safe_audio_filename("../recording.webm") == "recording.webm"
    assert safe_audio_filename("unsafe.exe") == "recording.webm"

from pathlib import Path

import pytest

from scripts.smoke_test import get_audio_content_type, normalize_base_url


def test_normalize_base_url_requires_https_for_remote_hosts() -> None:
    with pytest.raises(ValueError, match="must use HTTPS"):
        normalize_base_url("http://api.example.com", allow_http=True)

    assert normalize_base_url("https://api.example.com/", allow_http=False) == "https://api.example.com"


def test_normalize_base_url_allows_explicit_local_http() -> None:
    assert normalize_base_url("http://127.0.0.1:8000", allow_http=True) == "http://127.0.0.1:8000"


def test_audio_content_type_uses_backend_compatible_types() -> None:
    assert get_audio_content_type(Path("sample.webm")) == "audio/webm"
    assert get_audio_content_type(Path("sample.m4a")) == "audio/mp4"

    with pytest.raises(ValueError, match="unsupported audio extension"):
        get_audio_content_type(Path("sample.txt"))

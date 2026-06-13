"""Smoke-test a deployed Voice Dictation backend."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from urllib.parse import urlparse

import httpx


AUDIO_CONTENT_TYPES = {
    ".m4a": "audio/mp4",
    ".mp3": "audio/mpeg",
    ".mp4": "audio/mp4",
    ".ogg": "audio/ogg",
    ".wav": "audio/wav",
    ".webm": "audio/webm",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", help="Deployed backend base URL, such as https://api.example.com")
    parser.add_argument("--audio", type=Path, help="Optional audio file for a real transcription check")
    parser.add_argument("--allow-http", action="store_true", help="Allow HTTP for local smoke testing only")
    return parser.parse_args()


def normalize_base_url(value: str, *, allow_http: bool) -> str:
    url = urlparse(value.rstrip("/"))

    if not url.netloc or url.scheme not in {"http", "https"}:
        raise ValueError("base_url must be an absolute HTTP or HTTPS URL")
    if url.username or url.password or url.query or url.fragment:
        raise ValueError("base_url must not include credentials, a query, or a fragment")
    if url.scheme == "http" and (not allow_http or url.hostname not in {"127.0.0.1", "localhost", "::1"}):
        raise ValueError("deployed backends must use HTTPS; --allow-http is limited to localhost")

    return value.rstrip("/")


def get_audio_content_type(path: Path) -> str:
    try:
        return AUDIO_CONTENT_TYPES[path.suffix.lower()]
    except KeyError as exc:
        supported = ", ".join(sorted(AUDIO_CONTENT_TYPES))
        raise ValueError(f"unsupported audio extension; expected one of: {supported}") from exc


def main() -> int:
    args = parse_args()

    try:
        base_url = normalize_base_url(args.base_url, allow_http=args.allow_http)
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    try:
        with httpx.Client(timeout=45.0, follow_redirects=True) as client:
            health_response = client.get(f"{base_url}/health")
            health_response.raise_for_status()

            if health_response.json() != {"status": "ok"}:
                print("Health check returned an unexpected response.", file=sys.stderr)
                return 1

            print(f"PASS health: {base_url}/health")

            if args.audio is None:
                print("SKIP transcription: no --audio file supplied")
                return 0

            if not args.audio.is_file():
                print(f"Audio file not found: {args.audio}", file=sys.stderr)
                return 2

            content_type = get_audio_content_type(args.audio)
            with args.audio.open("rb") as audio_file:
                response = client.post(
                    f"{base_url}/api/transcribe",
                    files={"file": (args.audio.name, audio_file, content_type)},
                )
            response.raise_for_status()
            transcript = response.json().get("transcript")

            if not isinstance(transcript, str) or not transcript.strip():
                print("Transcription returned no transcript.", file=sys.stderr)
                return 1

            print(f"PASS transcription: {transcript}")
            return 0
    except (httpx.HTTPError, ValueError) as exc:
        print(f"Smoke test failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

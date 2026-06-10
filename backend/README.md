# Backend

This folder contains the FastAPI backend for the Voice Dictation Browser Extension.

The backend accepts audio from the browser extension, calls xAI Speech-to-Text, and returns transcripts.

The `/api/transcribe` endpoint validates the uploaded audio file, sends it to xAI from the backend only, and returns the transcript. The browser extension must never call xAI directly.

## Stack

- Python
- FastAPI
- httpx
- python-dotenv

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bat
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local environment file:

```bash
cp .env.example .env
```

Set `XAI_API_KEY` in `.env` before using `/api/transcribe`.

For local extension testing, keep `BACKEND_CORS_ORIGINS` limited to trusted local origins. Do not use `*` in production.

Run the development server:

```bash
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Transcription test:

```bash
curl -X POST http://127.0.0.1:8000/api/transcribe \
  -F "file=@sample.webm;type=audio/webm"
```

Run backend tests:

```bash
pytest
```

## Troubleshooting

- `503 Speech-to-text service is not configured.` means `XAI_API_KEY` is missing from `.env` or the backend was not restarted after editing `.env`.
- `502 Speech-to-text service failed.` means the backend reached xAI but xAI rejected or failed the request. Check backend logs for `xAI STT` warning lines.
- `403` from xAI usually means the xAI team needs credits, licenses, or Speech-to-Text access.
- `400 Unsupported audio file type.` means the uploaded file MIME type is not in the allowed audio list.
- Never paste or commit the real `XAI_API_KEY`.

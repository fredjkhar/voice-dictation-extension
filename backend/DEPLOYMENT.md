# Backend Deployment

This guide prepares the FastAPI backend for deployment. It does not cover a specific hosting provider.

## Required Environment Variables

- `XAI_API_KEY`: real xAI API key. Required for `/api/transcribe`.
- `XAI_API_BASE_URL`: defaults to `https://api.x.ai`.
- `APP_ENV`: set to `production` in deployed environments.
- `BACKEND_CORS_ORIGINS`: comma-separated origins allowed to call the backend.

Never place a real `XAI_API_KEY` in source control, Docker images, frontend code, or Chrome extension files.

## Docker Build

From the `backend/` folder:

```bash
docker build -t voice-dictation-backend .
```

Docker Desktop or another Docker daemon must be running before this command will work.

## Docker Run

```bash
docker run --rm -p 8000:8000 \
  -e XAI_API_KEY="replace_with_real_key" \
  -e XAI_API_BASE_URL="https://api.x.ai" \
  -e APP_ENV="production" \
  -e BACKEND_CORS_ORIGINS="chrome-extension://YOUR_EXTENSION_ID,https://YOUR_FRONTEND_ORIGIN" \
  voice-dictation-backend
```

For local Docker testing with the unpacked extension:

```bash
docker run --rm -p 8000:8000 \
  --env-file .env \
  voice-dictation-backend
```

## Health Check

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Extension Configuration

After the backend is deployed:

1. Open the extension popup.
2. Set Backend URL to the deployed HTTPS endpoint ending in `/api/transcribe`.
3. Save settings.
4. Reload the test page and run a short dictation test.

The extension must call only your backend. It must never call xAI directly.

## Production Notes

- Use HTTPS for deployed backends.
- Keep `BACKEND_CORS_ORIGINS` narrow.
- Keep `XAI_API_KEY` in the hosting provider's secret manager or environment variable system.
- Do not store raw audio by default.
- Monitor `502` responses and backend logs for xAI upstream failures.
- Consider adding rate limiting before broader use.

import json
import logging
import time
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings
from app.routes import transcribe

REQUEST_ID_HEADER = "X-Request-ID"
logger = logging.getLogger("app.requests")

app = FastAPI(title="Voice Dictation Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", REQUEST_ID_HEADER],
    expose_headers=[REQUEST_ID_HEADER],
)


def get_request_id(request: Request) -> str:
    incoming_request_id = request.headers.get(REQUEST_ID_HEADER)
    if incoming_request_id and 1 <= len(incoming_request_id) <= 80 and incoming_request_id.isprintable():
        return incoming_request_id

    return uuid4().hex


def get_oversized_upload_response(request: Request) -> JSONResponse | None:
    if request.method != "POST" or request.url.path != "/api/transcribe":
        return None

    if settings.max_transcribe_content_length_bytes <= 0:
        return None

    content_length = request.headers.get("content-length")
    if not content_length:
        return None

    try:
        parsed_content_length = int(content_length)
    except ValueError:
        return None

    if parsed_content_length <= settings.max_transcribe_content_length_bytes:
        return None

    return JSONResponse(
        status_code=413,
        content={"detail": "Uploaded audio file is too large."},
    )


def log_request(request: Request, response: Response, request_id: str, started_at: float) -> None:
    latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
    logger.info(
        json.dumps(
            {
                "event": "http_request",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "latency_ms": latency_ms,
            },
            separators=(",", ":"),
        )
    )


@app.middleware("http")
async def add_request_context(request: Request, call_next) -> Response:
    request_id = get_request_id(request)
    request.state.request_id = request_id
    started_at = time.perf_counter()

    try:
        response = get_oversized_upload_response(request)
        if response is None:
            response = await call_next(request)
    except Exception:
        latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.exception(
            json.dumps(
                {
                    "event": "http_request",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status": 500,
                    "latency_ms": latency_ms,
                },
                separators=(",", ":"),
            )
        )
        raise

    response.headers[REQUEST_ID_HEADER] = request_id
    log_request(request, response, request_id, started_at)
    return response


app.include_router(transcribe.router, prefix="/api")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

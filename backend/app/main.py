import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db.models import Base
from app.db.session import engine
from app.routers import audit, dashboard, inventory, matches, recalls
from app.security import InMemoryRateLimiter, client_key, rate_limit_bucket

logger = logging.getLogger(__name__)
settings = get_settings()
rate_limiter = InMemoryRateLimiter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


is_production = settings.app_env.lower() == "production"
app = FastAPI(
    title="RecallRadar AI API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(recalls.router)
app.include_router(inventory.router)
app.include_router(matches.router)
app.include_router(dashboard.router)
app.include_router(audit.router)


@app.middleware("http")
async def enforce_request_limits(request: Request, call_next):
    if request.method == "OPTIONS" or request.url.path == "/health":
        return await call_next(request)
    if request.url.path == "/inventory/upload":
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > settings.max_upload_bytes + (1024 * 1024):
            return JSONResponse(
                status_code=413,
                content={"detail": "Inventory upload is too large"},
            )
    return await call_next(request)


@app.middleware("http")
async def enforce_rate_limits(request: Request, call_next):
    if request.method == "OPTIONS" or request.url.path == "/health":
        return await call_next(request)
    bucket = rate_limit_bucket(request.method, request.url.path)
    limit = settings.rate_limit_per_window[bucket]
    decision = rate_limiter.check(
        client_key(request),
        bucket,
        limit,
        settings.rate_limit_window_seconds,
    )
    if not decision.allowed:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again shortly."},
            headers={"Retry-After": str(decision.retry_after_seconds)},
        )
    return await call_next(request)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "The request could not be validated."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled API error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred."},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

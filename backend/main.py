"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from db.session import engine, init_db
from rag.ingest import ensure_chroma_directory
from routes import auth, chat, document, health, query, test_db
from services import file_service

logger = logging.getLogger(__name__)

# Ensure uvicorn/FastAPI loggers show our messages
if not logging.root.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

# Browser origins for local Next.js (localhost vs 127.0.0.1 are different origins)
CORS_ALLOW_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    logger.info("Starting AI Knowledge Assistant API")
    logger.info("CORS allow_origins: %s", CORS_ALLOW_ORIGINS)
    print("[startup] CORS allow_origins:", CORS_ALLOW_ORIGINS)
    file_service.ensure_upload_directory()
    ensure_chroma_directory()
    if settings.auto_create_tables:
        init_db()
    print("[startup] Server ready — docs at http://127.0.0.1:8000/docs")
    logger.info("Application startup complete")
    yield
    engine.dispose()
    logger.info("Application shutdown")


app = FastAPI(
    title="AI Knowledge Assistant API",
    version="0.1.0",
    description="Backend API for the ai-knowledge-assistant monorepo.",
    lifespan=lifespan,
)

# CRITICAL: CORS must be added immediately after FastAPI() and BEFORE include_router.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = "/api"


@app.get(f"{api_prefix}/test")
def api_test() -> dict[str, str]:
    """Debug: confirms /api routing + CORS preflight path without DB."""
    return {"message": "API working"}


app.include_router(health.router, prefix=api_prefix)
app.include_router(chat.router, prefix=api_prefix)
app.include_router(document.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)
app.include_router(test_db.router, prefix=api_prefix)
app.include_router(query.router, prefix=api_prefix)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "ai-knowledge-assistant"}

"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from db.session import engine, init_db
from routes import auth, chat, document, health, test_db
from services import file_service


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    file_service.ensure_upload_directory()
    if settings.auto_create_tables:
        init_db()
    yield
    engine.dispose()


app = FastAPI(
    title="AI Knowledge Assistant API",
    version="0.1.0",
    description="Backend API for the ai-knowledge-assistant monorepo.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = "/api"
app.include_router(health.router, prefix=api_prefix)
app.include_router(chat.router, prefix=api_prefix)
app.include_router(document.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)
app.include_router(test_db.router, prefix=api_prefix)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "ai-knowledge-assistant"}

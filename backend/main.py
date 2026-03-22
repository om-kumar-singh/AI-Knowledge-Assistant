"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import health

app = FastAPI(
    title="AI Knowledge Assistant API",
    version="0.1.0",
    description="Backend API for the ai-knowledge-assistant monorepo.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "ai-knowledge-assistant"}

"""Application settings loaded from environment variables."""

from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Runtime configuration; values can be set via `.env` or the process environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    database_url: str = "postgresql://localhost:5432/ai_knowledge_assistant"
    database_echo: bool = False
    auto_create_tables: bool = False
    uploads_dir: str = "uploads"
    chroma_persist_dir: str = "chroma_data"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    rag_default_top_k: int = 5
    llm_model_name: str = "google/flan-t5-base"
    llm_max_new_tokens: int = 200
    llm_max_context_chars: int = 2000
    llm_max_history_chars: int = 1500
    chat_history_limit: int = 10
    # Comma-separated browser origins (http://localhost:3000 vs http://127.0.0.1:3000 differ for CORS).
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    def cors_origins_list(self) -> list[str]:
        parts = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        return parts if parts else ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()

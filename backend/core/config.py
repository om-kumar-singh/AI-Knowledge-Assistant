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


@lru_cache
def get_settings() -> Settings:
    return Settings()

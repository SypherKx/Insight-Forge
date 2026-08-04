"""
Backend configuration.

Environment-based configuration using pydantic-settings.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "InsightForge AI"
    app_version: str = "1.0.0"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    # Database
    database_url: str = "sqlite:///./insightforge.db"

    # File storage
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 500

    # LLM
    llm_provider: str = "groq"
    llm_model: str = "llama-3.3-70b-versatile"
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # RAG
    rag_index_path: str = "./rag_index"
    rag_enabled: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_origin_list(self) -> list:
        return [o.strip() for o in self.cors_origins.split(",")]

    def ensure_dirs(self):
        """Create necessary directories."""
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)
        Path(self.rag_index_path).parent.mkdir(parents=True, exist_ok=True)


settings = Settings()

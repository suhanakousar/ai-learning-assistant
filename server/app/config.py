"""
Application configuration loaded from environment variables.
"""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralized settings for the AI Learning Assistant API."""

    # LLM
    llm_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    # Grok (xAI) - OpenAI-compatible
    grok_api_key: str = ""
    grok_model: str = "grok-4-fast-reasoning"
    # Google Gemini
    google_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # Embeddings
    embeddings_provider: str = "openai"
    openai_embeddings_model: str = "text-embedding-3-small"
    ollama_embeddings_model: str = "nomic-embed-text"
    google_embeddings_model: str = "models/gemini-embedding-001"

    # Document QA
    document_chunk_size: int = 1000
    document_chunk_overlap: int = 200

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "info"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()

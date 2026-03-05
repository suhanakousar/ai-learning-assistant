"""
Embeddings utility for Document QA.
Provides a unified interface for OpenAI, Google (Gemini), or Ollama embeddings.
"""

from typing import List

from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings

from app.config import get_settings


def get_embeddings_model():
    """
    Return the configured embeddings model based on EMBEDDINGS_PROVIDER.
    Supports: openai, google (Gemini - uses GOOGLE_API_KEY), ollama.
    """
    settings = get_settings()
    provider = (settings.embeddings_provider or "openai").strip().lower()

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when EMBEDDINGS_PROVIDER=openai. "
                "Set it in your .env file, or use EMBEDDINGS_PROVIDER=google to use your Gemini key."
            )
        return OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model=settings.openai_embeddings_model,
        )

    if provider == "google":
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
        except ImportError:
            raise ValueError(
                "Install langchain-google-genai for Google embeddings: pip install langchain-google-genai"
            )
        if not settings.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY is required when EMBEDDINGS_PROVIDER=google. Set it in your .env file."
            )
        return GoogleGenerativeAIEmbeddings(
            google_api_key=settings.google_api_key,
            model=settings.google_embeddings_model,
        )

    if provider == "ollama":
        return OllamaEmbeddings(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embeddings_model,
        )

    raise ValueError(
        f"Unsupported EMBEDDINGS_PROVIDER: {provider}. "
        "Use 'openai', 'google', or 'ollama'."
    )


def embed_texts(embeddings, texts: List[str]) -> List[List[float]]:
    """Embed a list of texts. Convenience wrapper."""
    return embeddings.embed_documents(texts)

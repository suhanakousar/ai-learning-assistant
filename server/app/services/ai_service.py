"""
Central AI/LLM service.
Provides a single entry point for the configured LLM (OpenAI, OpenRouter, Ollama, Grok, or Gemini).
"""

from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings


def get_llm():
    """
    Return the configured LangChain LLM based on LLM_PROVIDER.
    Supports: openai, openrouter, ollama, grok (xAI), gemini (Google).
    """
    settings = get_settings()
    provider = (settings.llm_provider or "openai").strip().lower()

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai. Set it in .env"
            )
        return ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=0.3,
        )

    if provider == "openrouter":
        if not settings.openrouter_api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is required when LLM_PROVIDER=openrouter. Set it in .env"
            )
        return ChatOpenAI(
            openai_api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            model=settings.openrouter_model,
            temperature=0.3,
        )

    if provider == "ollama":
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=0.3,
        )

    if provider == "grok":
        if not settings.grok_api_key:
            raise ValueError(
                "GROK_API_KEY is required when LLM_PROVIDER=grok. Set it in .env"
            )
        return ChatOpenAI(
            openai_api_key=settings.grok_api_key,
            base_url="https://api.x.ai/v1",
            model=settings.grok_model,
            temperature=0.3,
        )

    if provider == "gemini":
        if not settings.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY is required when LLM_PROVIDER=gemini. Set it in .env"
            )
        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            api_key=settings.google_api_key,
            temperature=0.3,
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {provider}. Use openai, openrouter, ollama, grok, or gemini."
    )

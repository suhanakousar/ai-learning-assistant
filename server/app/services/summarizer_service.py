"""
Text summarization service.
Uses structured prompts to produce concise summaries under 100 words.
"""

from langchain_core.messages import SystemMessage, HumanMessage

from app.services.ai_service import get_llm
from app.utils.prompt_templates import SUMMARIZE_SYSTEM, SUMMARIZE_USER
from app.utils.llm_retry import invoke_with_retry


def summarize_text(text: str) -> str:
    """
    Summarize long text into a concise summary (under 100 words).
    Uses a professional academic summarizer role and guardrails against hallucination.
    """
    if not text or not text.strip():
        return "No valid text was provided to summarize."

    llm = get_llm()
    messages = [
        SystemMessage(content=SUMMARIZE_SYSTEM),
        HumanMessage(content=SUMMARIZE_USER.format(text=text.strip())),
    ]
    response = invoke_with_retry(llm, messages)
    summary = response.content.strip() if hasattr(response, "content") else str(response).strip()
    return summary

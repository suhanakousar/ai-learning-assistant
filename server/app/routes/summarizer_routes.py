"""
Text summarization API routes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.summarizer_service import summarize_text

router = APIRouter(prefix="/api", tags=["Summarization"])


class SummarizeRequest(BaseModel):
    """Request body for POST /api/summarize."""

    text: str = Field(..., description="Long paragraph or article to summarize", min_length=1)


class SummarizeResponse(BaseModel):
    """Response for POST /api/summarize."""

    summary: str = Field(..., description="Concise summary under 100 words")


@router.post("/summarize", response_model=SummarizeResponse)
def api_summarize(request: SummarizeRequest):
    """
    Summarize long text into a concise explanation (under 100 words).
    Uses a professional academic summarizer prompt with anti-hallucination guardrails.
    """
    try:
        summary = summarize_text(request.text)
        return SummarizeResponse(summary=summary)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

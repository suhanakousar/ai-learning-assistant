"""
Document Question Answering API routes.
Accepts PDF upload and a question, returns an answer based only on document content.
"""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.services.document_qa_service import answer_document_question

router = APIRouter(prefix="/api", tags=["Document QA"])


class DocumentQAResponse(BaseModel):
    """Response for POST /api/document-qa."""

    answer: str = Field(..., description="Answer generated based only on document content")


@router.post("/document-qa", response_model=DocumentQAResponse)
async def api_document_qa(
    document: UploadFile = File(..., description="PDF file"),
    question: str = Form(..., description="User question about the document"),
):
    """
    Upload a PDF and ask a question. The answer is generated using only the document content.
    Uses PyPDFLoader, chunking, FAISS embeddings, and RetrievalQA. Responds with
    "Information not found in the document" when the answer is not in the document.
    """
    if not document.filename or not document.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    try:
        pdf_bytes = await document.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        answer = answer_document_question(pdf_bytes, question)
        return DocumentQAResponse(answer=answer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document QA failed: {str(e)}")

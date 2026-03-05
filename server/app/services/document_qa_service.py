"""
Document Question Answering service.
Loads PDF with PyPDFLoader, chunks text, builds FAISS index, and uses retrieval chain.
"""

import tempfile
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

from app.config import get_settings
from app.services.ai_service import get_llm
from app.utils.embeddings import get_embeddings_model
from app.utils.prompt_templates import DOCUMENT_QA_SYSTEM, DOCUMENT_QA_USER


def _get_text_splitter():
    """Return configured text splitter for document chunks."""
    settings = get_settings()
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.document_chunk_size,
        chunk_overlap=settings.document_chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def _format_docs(docs):
    """Format retrieved documents as a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


def answer_document_question(pdf_content: bytes, question: str) -> str:
    """
    Load PDF from bytes, split into chunks, embed with FAISS, and answer the question
    using only document content. Returns "Information not found in the document" when uncertain.
    """
    if not pdf_content or len(pdf_content) == 0:
        return "No document was provided."

    question = (question or "").strip()
    if not question:
        return "No question was provided."

    # Write PDF to a temporary file (PyPDFLoader expects a path)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_content)
        tmp_path = tmp.name

    try:
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    if not documents:
        return "The document could not be read or contains no text."

    text_splitter = _get_text_splitter()
    splits = text_splitter.split_documents(documents)

    if not splits:
        return "Information not found in the document."

    embeddings = get_embeddings_model()
    vectorstore = FAISS.from_documents(splits, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    # Prompt uses "context" (retrieved docs) and "query" (user question)
    prompt_template = DOCUMENT_QA_SYSTEM + "\n\n" + DOCUMENT_QA_USER
    prompt = ChatPromptTemplate.from_template(prompt_template)

    llm = get_llm()

    # LCEL: retrieve -> format context + pass query -> prompt -> LLM -> string
    chain = (
        RunnableParallel(
            context=retriever | _format_docs,
            query=RunnablePassthrough(),
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    result = chain.invoke(question)
    answer = (result or "").strip()
    return answer or "Information not found in the document."

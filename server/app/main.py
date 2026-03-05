"""
AI Learning Assistant – FastAPI application entry point.
Modular AI microservices for summarization, document QA, and learning path generation.
"""

from pathlib import Path

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.routes import document_routes, learning_routes, summarizer_routes

# Path to static assets (UI)
STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    yield
    # Cleanup if needed (e.g., close LLM clients)


app = FastAPI(
    title="AI Learning Assistant API",
    description="Modular AI microservices: Text Summarization, Document QA, Learning Path Generator",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(summarizer_routes.router)
app.include_router(document_routes.router)
app.include_router(learning_routes.router)


@app.get("/")
def index():
    """Serve the web UI."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return api_info()


@app.get("/api-info")
def api_info():
    """API info (JSON) for programmatic access."""
    return {
        "service": "AI Learning Assistant",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "POST /api/summarize",
            "POST /api/document-qa",
            "POST /api/learning-path",
        ],
    }


@app.get("/health")
def health():
    """Health check for load balancers and monitoring."""
    return {"status": "ok"}

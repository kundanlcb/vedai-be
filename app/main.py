# app/main.py
import warnings
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Suppress harmless deprecation warnings from LangChain trying to use pydantic v1
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_core._api.deprecation")
warnings.filterwarnings("ignore", category=UserWarning, message=".*orm_mode.*")

# ✅ Ensure models are imported so SQLModel.metadata includes all tables
import app.models  # noqa: F401

from app.db import init_db
from app.settings import settings

# ✅ Routers
from app.routes.content import router as content_router
from app.routes.question import router as question_router
from app.routes.ingest import router as ingest_router
from app.routes.chat import router as chat_router
from app.routes.auth import router as auth_router
from app.routes.student import router as student_router
from app.routes.progress import router as progress_router
from app.routes.tests import router as tests_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Modern replacement for startup/shutdown events.
    Handles database initialization and other resource setup/cleanup.
    """
    # Startup logic
    await init_db()
    print("✅ Database initialized")

    yield  # App is now running

    # Shutdown logic
    print("🛑 Application shutdown complete")


# ✅ Initialize FastAPI app with comprehensive OpenAPI metadata
app = FastAPI(
    title="VedAI Backend API",
    version="1.0.0",
    description="""
## VedAI - Intelligent Student Learning Platform Backend

A comprehensive FastAPI backend providing AI-powered learning features for students.

### Key Features

* **🔐 Authentication & Authorization** - Secure JWT-based authentication
* **👨‍🎓 Student Management** - Profile creation and management
* **📚 Content Management** - PDF upload, processing, and retrieval
* **❓ Question Bank** - Multi-format questions (MCQ, Short, Long, Numerical)
* **📊 Progress Tracking** - Chapter-wise progress monitoring
* **📝 Mock Tests** - Create, attempt, and auto-grade tests
* **💬 AI Chat (RAG)** - Question answering with Gemini AI and vector search

### Tech Stack

* **Framework:** FastAPI
* **Database:** PostgreSQL with pgvector
* **AI/ML:** LangChain, Google Gemini, Sentence Transformers
* **Authentication:** JWT (python-jose)
* **ORM:** SQLModel (SQLAlchemy 2.0)

### API Documentation

* **Swagger UI:** [/docs](/docs) - Interactive API documentation
* **ReDoc:** [/redoc](/redoc) - Alternative documentation view
    """,
    contact={
        "name": "VedAI Development Team",
        "email": "support@vedai.example.com",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://vedai.example.com/license",
    },
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User authentication operations including login and registration. Returns JWT tokens for secure API access.",
        },
        {
            "name": "Students",
            "description": "Student profile management operations. Create, read, update, and delete student profiles with class, subjects, and board information.",
        },
        {
            "name": "Content",
            "description": "Content management operations for PDFs. Upload, ingest, and search educational content with vector embeddings.",
        },
        {
            "name": "Questions",
            "description": "Question bank operations. Manage MCQs, short answer, long answer, and numerical questions with metadata filtering.",
        },
        {
            "name": "Ingest",
            "description": "PDF ingestion pipeline. Process and chunk PDFs into searchable content with intelligent text splitting.",
        },
        {
            "name": "Chat",
            "description": "AI-powered chat using Retrieval-Augmented Generation (RAG). Ask questions and get answers with source citations from ingested content.",
        },
        {
            "name": "Progress",
            "description": "Student progress tracking. Monitor chapter-wise completion, time spent, and subject-wise statistics.",
        },
        {
            "name": "Tests",
            "description": "Mock test management and attempts. Create tests, start attempts, auto-save drafts, submit answers, and view performance statistics.",
        },
    ],
    lifespan=lifespan,
    swagger_ui_parameters={
        "deepLinking": True,
        "displayRequestDuration": True,
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
        "defaultModelsExpandDepth": 2,
        "defaultModelExpandDepth": 2,
        "docExpansion": "list",
        "persistAuthorization": True,
    },
    redoc_url="/redoc",
    docs_url="/docs",
)

# ✅ Register routers
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(student_router, prefix="/api", tags=["Students"])
app.include_router(content_router, prefix="/api", tags=["Content"])
app.include_router(question_router, prefix="/api", tags=["Questions"])
app.include_router(ingest_router, prefix="/api", tags=["Ingest"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(progress_router, prefix="/api", tags=["Progress"])
app.include_router(tests_router, prefix="/api", tags=["Tests"])

# Root endpoints
@app.get("/")
async def root():
    return {"status": "ok", "message": "VedAI backend is running 🚀"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
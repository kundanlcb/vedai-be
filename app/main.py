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


# ✅ Initialize FastAPI app
app = FastAPI(
    title=getattr(settings, "APP_NAME", "VedAI"),
    lifespan=lifespan,
)

# ✅ Register routers
app.include_router(content_router, prefix="/api", tags=["Content"])
app.include_router(question_router, prefix="/api", tags=["Questions"])
app.include_router(ingest_router, prefix="/api", tags=["Ingest"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])

# Root endpoints
@app.get("/")
async def root():
    return {"status": "ok", "message": "VedAI backend is running 🚀"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
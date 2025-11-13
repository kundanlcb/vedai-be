# app/routes/__init__.py
from .content import router as content
from .question import router as question
from .ingest import router as ingest

__all__ = ["question","content", "ingest"]
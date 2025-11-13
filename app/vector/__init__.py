# app/vector/__init__.py
"""
Vector store utilities — provides helpers to persist and query embeddings.
Currently backed by PGVector via SQLModel.
"""

from app.vector.store import save_embeddings

__all__ = ["save_embeddings"]
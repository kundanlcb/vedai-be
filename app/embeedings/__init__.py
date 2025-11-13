# app/embeddings/__init__.py
"""
Embeddings module — provides local and (optionally) remote embedding backends.
Exposes a unified interface for text embeddings.
"""

from app.embeedings.local import embed_texts

__all__ = ["embed_texts"]
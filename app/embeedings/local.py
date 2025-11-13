# app/embeddings/local.py
"""
Local embeddings adapter using sentence-transformers.
Provides an async-friendly `embed_texts` function that returns list[list[float]].
The model is loaded lazily on first call to avoid startup cost.
"""
from typing import List
import asyncio
from functools import lru_cache, partial


# Lazy import to avoid heavy startup cost when running tests or other commands
def _load_model(name: str = "all-MiniLM-L6-v2"):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(name)


@lru_cache(maxsize=1)
def _get_model(name: str = "all-MiniLM-L6-v2"):
    return _load_model(name)


async def embed_texts(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> List[List[float]]:
    """Embed a batch of texts asynchronously using a threadpool.

    Returns list of vectors aligned with `texts`.
    """
    model = _get_model(model_name)
    loop = asyncio.get_event_loop()

    # Run blocking encode in threadpool; use partial to pass normalize_embeddings as keyword arg
    encode_fn = partial(model.encode, normalize_embeddings=True)
    vectors = await loop.run_in_executor(None, encode_fn, texts)
    try:
        return vectors.tolist()
    except Exception:
        return [list(v) for v in vectors]
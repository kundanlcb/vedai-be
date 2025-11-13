# app/schemas/chat.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List


class ChatRequest(BaseModel):
    """Schema for chat question request."""
    question: str = Field(..., min_length=1, max_length=500, description="User question")
    class_name: Optional[int] = Field(None, description="Filter by class (8-12)")
    subject: Optional[str] = Field(None, description="Filter by subject")
    chapter: Optional[str] = Field(None, description="Filter by chapter")
    top_k: int = Field(8, ge=1, le=50, description="Number of chunks to retrieve")
    re_rank: bool = Field(False, description="Enable reranking of results")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "question": "Why do tides happen?",
            "class_name": 10,
            "subject": "Science",
            "chapter": "Tides",
            "top_k": 8,
            "re_rank": False
        }
    })


class SourceChunk(BaseModel):
    """Schema for source information in response."""
    chunk_id: int
    source_file: Optional[str] = None
    page: Optional[int] = None
    snippet: str
    similarity_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class LLMUsage(BaseModel):
    """Schema for LLM usage metrics."""
    latency_ms: float
    input_tokens: int
    output_tokens: int


class ChatResponse(BaseModel):
    """Schema for chat response."""
    answer: str
    sources: List[SourceChunk]
    metadata: dict = Field(default_factory=dict)
    llm_usage: Optional[LLMUsage] = None
    error: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "answer": "Tides occur due to the gravitational pull of the moon and sun... [1]",
            "sources": [
                {
                    "chunk_id": 123,
                    "source_file": "10th-science.pdf",
                    "page": 12,
                    "snippet": "Tides are caused by gravity...",
                    "similarity_score": 0.92
                }
            ],
            "metadata": {
                "retrieved_count": 50,
                "used_top_k": 8,
                "re_ranked": False
            },
            "llm_usage": {
                "latency_ms": 1200,
                "input_tokens": 256,
                "output_tokens": 128
            }
        }
    })


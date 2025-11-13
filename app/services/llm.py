# app/services/llm.py
import time
from typing import List, Tuple
from langchain_core.prompts import PromptTemplate

from app.settings import settings
from app.logger import get_logger

logger = get_logger(__name__)


class LLMConfig:
    """Configuration for LLM calls."""
    TEMPERATURE: float = 0.1
    MAX_OUTPUT_TOKENS: int = 512
    TIMEOUT_SECONDS: int = 30
    MAX_RETRIES: int = 3


def get_llm():
    """Initialize Gemini API (lazy loaded to avoid Python 3.14 protobuf issues)."""
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not configured")

    # Lazy import to avoid module-level import issues with protobuf on Python 3.14
    import google.generativeai as genai

    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={
            "temperature": LLMConfig.TEMPERATURE,
            "max_output_tokens": LLMConfig.MAX_OUTPUT_TOKENS,
        }
    )
    return model


def get_prompt_template() -> PromptTemplate:
    """Get prompt template for QA."""
    template = """You are a helpful assistant answering questions based ONLY on the provided textbook excerpts.
Always cite sources like [1], [2], etc. using the source numbers provided.
If the answer is not found in the provided context, respond: "I don't know based on provided texts."
Be concise and accurate.

-- CONTEXT START --
{context}
-- CONTEXT END --

Question: {question}

Answer:"""

    return PromptTemplate(
        input_variables=["context", "question"],
        template=template,
    )


async def generate_answer(
    question: str,
    context_snippets: List[str],
    context_metadata: List[dict],
) -> Tuple[str, float, int, int]:
    """
    Generate answer using Gemini with context snippets.

    Args:
        question: User question
        context_snippets: List of relevant text snippets
        context_metadata: Metadata for each snippet

    Returns:
        Tuple of (answer, latency_ms, input_tokens, output_tokens)
    """
    try:
        model = get_llm()
        prompt_template = get_prompt_template()
        context = _build_context(context_snippets, context_metadata)

        # Format the prompt
        prompt_text = prompt_template.format(context=context, question=question)

        start_time = time.time()
        response = model.generate_content(prompt_text)
        latency_ms = (time.time() - start_time) * 1000

        answer = response.text
        tokens_in = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
        tokens_out = response.usage_metadata.candidates_token_count if response.usage_metadata else 0

        logger.info(
            "LLM answer generated",
            extra={
                "latency_ms": latency_ms,
                "input_tokens": tokens_in,
                "output_tokens": tokens_out,
            }
        )

        return answer, latency_ms, tokens_in, tokens_out

    except Exception as e:
        logger.error("Error generating answer", extra={"error": str(e)}, exc_info=True)
        raise


def _build_context(snippets: List[str], metadata: List[dict]) -> str:
    """Build context string from snippets and metadata."""
    context_lines = []

    for i, (snippet, meta) in enumerate(zip(snippets, metadata), 1):
        source_info = f"[{i}]"
        if meta.get("source_file"):
            source_info += f" (file: {meta['source_file']}"
        if meta.get("page"):
            source_info += f" page: {meta['page']}"
        if meta.get("source_file") or meta.get("page"):
            source_info += ")"

        context_lines.append(f"{source_info} {snippet}")

    return "\n".join(context_lines)


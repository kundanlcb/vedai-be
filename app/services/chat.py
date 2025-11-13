# app/services/chat.py
import time
from langchain_core.prompts import PromptTemplate

from app.services.rag import retrieve_context
from app.schemas.chat import ChatRequest, ChatResponse, SourceChunk, LLMUsage
from app.settings import settings
from app.logger import get_logger

logger = get_logger(__name__)

FALLBACK_MESSAGE = "I don't know based on provided texts."


def get_llm():
    """Get Gemini LLM (lazy loaded)."""
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not configured")

    import google.generativeai as genai
    genai.configure(api_key=settings.GOOGLE_API_KEY)

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={
            "temperature": 0.1,
            "max_output_tokens": 512,
        }
    )
    return model


def get_prompt_template() -> PromptTemplate:
    """Get RAG prompt template."""
    template = """You are a helpful assistant answering questions based ONLY on the provided context.
Always cite sources using [1], [2], etc.
If the answer is not found in the context, respond: "I don't know based on provided texts."
Be concise and accurate.

Context:
{context}

Question: {question}

Answer:"""

    return PromptTemplate(
        input_variables=["context", "question"],
        template=template,
    )


async def answer_question(request: ChatRequest) -> ChatResponse:
    """Answer question using LangChain RAG with Gemini."""
    try:
        logger.info("Chat request", extra={"question": request.question[:50]})

        # Retrieve context
        docs = await retrieve_context(
            question=request.question,
            class_name=request.class_name,
            subject=request.subject,
            chapter=request.chapter,
            top_k=request.top_k,
        )

        if not docs:
            return ChatResponse(
                answer="No relevant information found in the database.",
                sources=[],
                metadata={"retrieved_count": 0, "used_top_k": request.top_k},
                error="No documents found",
            )

        # Build context
        context_text = _build_context(docs)

        # Generate answer
        logger.info("Generating answer")
        start_time = time.time()

        llm = get_llm()
        prompt_template = get_prompt_template()
        prompt = prompt_template.format(
            context=context_text,
            question=request.question,
        )

        response = llm.generate_content(prompt)
        latency_ms = (time.time() - start_time) * 1000
        answer = response.text

        tokens_in = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
        tokens_out = response.usage_metadata.candidates_token_count if response.usage_metadata else 0

        # Extract sources
        sources = [
            SourceChunk(
                chunk_id=i + 1,
                source_file=doc.metadata.get("source_file"),
                page=doc.metadata.get("page"),
                snippet=doc.page_content[:200],
            )
            for i, doc in enumerate(docs)
        ]

        logger.info("Answer generated", extra={"latency_ms": latency_ms})

        return ChatResponse(
            answer=answer,
            sources=sources,
            metadata={"retrieved_count": len(docs), "used_top_k": request.top_k},
            llm_usage=LLMUsage(
                latency_ms=latency_ms,
                input_tokens=tokens_in,
                output_tokens=tokens_out,
            ),
        )

    except Exception as e:
        logger.error("Error in RAG", extra={"error": str(e)}, exc_info=True)
        return ChatResponse(
            answer=FALLBACK_MESSAGE,
            sources=[],
            metadata={},
            error=str(e),
        )


def _build_context(docs: list) -> str:
    """Build context string from documents."""
    lines = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source_file", "Unknown")
        page = doc.metadata.get("page", "?")
        lines.append(f"[{i}] {source} (page {page}):\n{doc.page_content}")
    return "\n\n".join(lines)


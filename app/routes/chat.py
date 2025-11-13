# app/routes/chat.py
from fastapi import APIRouter, HTTPException, status
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import answer_question
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/ask", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def ask_question(request: ChatRequest) -> ChatResponse:
    """
    Answer a question using LangChain RAG with Gemini.

    - **question**: The student's question (required)
    - **class_name**: Filter by class 8-12 (optional)
    - **subject**: Filter by subject (optional)
    - **chapter**: Filter by chapter (optional)
    - **top_k**: Number of documents to retrieve (1-50, default 8)
    - **re_rank**: Enable reranking (optional)

    Returns structured answer with citations and sources.
    """
    try:
        logger.info(
            "Chat endpoint called",
            extra={
                "question_len": len(request.question),
                "has_filters": any([request.class_name, request.subject, request.chapter]),
            }
        )

        response = await answer_question(request)

        logger.info(
            "Chat response ready",
            extra={
                "has_error": response.error is not None,
                "sources": len(response.sources),
            }
        )

        return response

    except ValueError as e:
        logger.error("Invalid request", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Unexpected error", extra={"error": str(e)}, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


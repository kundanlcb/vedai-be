# app/services/rag.py
"""
End-to-end RAG service using LangChain.
Handles: PDF loading -> splitting -> embedding -> storing -> retrieval
"""
from typing import List, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document

from app.settings import settings
from app.logger import get_logger

logger = get_logger(__name__)


class RAGConfig:
    """Configuration for RAG pipeline."""
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    COLLECTION_NAME: str = "content_chunks"


def get_embeddings():
    """Get HuggingFace embeddings."""
    return HuggingFaceEmbeddings(model_name=RAGConfig.EMBEDDING_MODEL)


def get_vector_store():
    """Get PGVector store."""
    embeddings = get_embeddings()
    return PGVector(
        embeddings=embeddings,
        connection=settings.DATABASE_URL,
        collection_name=RAGConfig.COLLECTION_NAME,
    )


async def load_and_split_pdf(
    file_path: str,
    source_file: str,
    class_name: Optional[int] = None,
    subject: Optional[str] = None,
    chapter: Optional[str] = None,
) -> List[Document]:
    """Load PDF and split into documents."""
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=RAGConfig.CHUNK_SIZE,
            chunk_overlap=RAGConfig.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""],
        )

        docs = splitter.split_documents(pages)

        for doc in docs:
            doc.metadata.update({
                "source_file": source_file,
                "class_name": class_name,
                "subject": subject,
                "chapter": chapter,
            })

        logger.info(
            "PDF loaded and split",
            extra={"file": source_file, "chunk_count": len(docs)}
        )

        return docs

    except Exception as e:
        logger.error("Error loading PDF", extra={"error": str(e)}, exc_info=True)
        raise


async def store_embeddings(documents: List[Document]) -> dict:
    """Embed and store documents in PGVector."""
    try:
        vector_store = get_vector_store()
        ids = vector_store.add_documents(documents)

        logger.info("Embeddings stored", extra={"count": len(ids)})

        return {"inserted": len(ids), "skipped": 0}

    except Exception as e:
        logger.error("Error storing embeddings", extra={"error": str(e)}, exc_info=True)
        raise


async def retrieve_context(
    question: str,
    class_name: Optional[int] = None,
    subject: Optional[str] = None,
    chapter: Optional[str] = None,
    top_k: int = 8,
) -> List[Document]:
    """Retrieve relevant documents from PGVector."""
    try:
        vector_store = get_vector_store()

        filter_dict = {}
        if class_name is not None:
            filter_dict["class_name"] = class_name
        if subject is not None:
            filter_dict["subject"] = subject
        if chapter is not None:
            filter_dict["chapter"] = chapter

        if filter_dict:
            docs = vector_store.similarity_search(
                question, k=top_k, filter=filter_dict,
            )
        else:
            docs = vector_store.similarity_search(question, k=top_k)

        logger.info("Retrieved documents", extra={"count": len(docs)})
        return docs

    except Exception as e:
        logger.error("Error retrieving", extra={"error": str(e)}, exc_info=True)
        return []


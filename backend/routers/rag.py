"""
RAG router — Document upload and context retrieval.
"""

import logging
import tempfile
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException

from ..dependencies import get_rag_service
from ..models.requests import RAGQueryRequest
from ..models.responses import RAGQueryResponse, RAGUploadResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rag", tags=["RAG"])


@router.get("/stats")
async def get_rag_stats():
    """Get statistics about currently indexed documents and vectors."""
    rag_svc = get_rag_service()
    return rag_svc.get_stats()


@router.post("/clear")
@router.delete("/documents")
async def clear_rag_knowledge_base():
    """Clear all documents and vectors from the RAG knowledge base."""
    rag_svc = get_rag_service()
    return rag_svc.clear()


@router.post("/documents", response_model=RAGUploadResponse)
async def upload_rag_documents(files: List[UploadFile] = File(...)):
    """Upload documents to the RAG knowledge base."""
    rag_svc = get_rag_service()

    if not rag_svc.is_available:
        raise HTTPException(
            status_code=503,
            detail="RAG service not available. Install sentence-transformers and faiss-cpu."
        )

    upload_dir = Path("./uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_paths = []

    try:
        for file in files:
            safe_name = Path(file.filename).name
            target_path = upload_dir / safe_name
            content = await file.read()
            target_path.write_bytes(content)
            saved_paths.append(str(target_path))

        # Ingest documents into FAISS vector database
        stats = rag_svc.ingest_documents(saved_paths)

        return RAGUploadResponse(
            documents_ingested=stats.get("documents_ingested", 0),
            chunks_created=stats.get("chunks_created", 0),
            errors=stats.get("errors", 0),
        )
    except Exception as e:
        logger.exception(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest):
    """Query RAG knowledge base for relevant context and optional LLM synthesis."""
    rag_svc = get_rag_service()

    if not rag_svc.is_available:
        raise HTTPException(
            status_code=503,
            detail="RAG service not available."
        )

    result = rag_svc.query(
        query=request.query,
        top_k=request.top_k,
        min_score=request.min_score,
        filters=request.filters,
        model=request.model or "llama3.2:3b",
        generate_answer=request.generate_answer,
    )

    answer = result.get("answer")
    res_list = result.get("results", [])

    if not res_list and not answer:
        answer = "No relevant context found in your uploaded documents for this query. Upload more documents (.pdf, .txt, .md, .docx, .csv) to expand the knowledge base."

    return RAGQueryResponse(
        results=res_list,
        query=request.query,
        total_results=result.get("total_results", len(res_list)),
        answer=answer,
        llm_model=result.get("llm_model"),
        used_llm=result.get("used_llm", False),
    )

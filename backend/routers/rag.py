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


@router.post("/documents", response_model=RAGUploadResponse)
async def upload_rag_documents(files: List[UploadFile] = File(...)):
    """Upload documents to the RAG knowledge base."""
    rag_svc = get_rag_service()

    if not rag_svc.is_available:
        raise HTTPException(
            status_code=503,
            detail="RAG service not available. Install sentence-transformers and faiss-cpu."
        )

    # Save uploaded files temporarily
    temp_paths = []
    try:
        for file in files:
            suffix = Path(file.filename).suffix
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=suffix, dir="./uploads"
            ) as tmp:
                content = await file.read()
                tmp.write(content)
                temp_paths.append(tmp.name)

        # Ingest
        stats = rag_svc.ingest_documents(temp_paths)

        return RAGUploadResponse(
            documents_ingested=stats.get("documents_ingested", 0),
            chunks_created=stats.get("chunks_created", 0),
            errors=stats.get("errors", 0),
        )
    finally:
        # Cleanup temp files
        for p in temp_paths:
            try:
                Path(p).unlink(missing_ok=True)
            except Exception:
                pass


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest):
    """Query RAG knowledge base for relevant context."""
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
    )

    return RAGQueryResponse(
        results=result.get("results", []),
        query=request.query,
        total_results=result.get("total_results", 0),
    )

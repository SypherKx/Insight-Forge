"""
RAG Service — Manages document ingestion and retrieval.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

SRC_DIR = str(Path(__file__).resolve().parent.parent.parent / "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

logger = logging.getLogger(__name__)

# RAG is optional — gracefully degrade if dependencies missing
_RAG_AVAILABLE = False
_rag_pipeline = None

try:
    from rag.pipeline import RAGPipeline, create_pipeline
    _RAG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"RAG module not available: {e}. RAG features disabled.")


class RAGService:
    """Manages RAG document ingestion and retrieval."""

    def __init__(self, index_path: str = "./rag_index", org_id: str = "default"):
        self.index_path = index_path
        self.org_id = org_id
        self.pipeline = None

        if _RAG_AVAILABLE:
            try:
                self.pipeline = create_pipeline(
                    index_path=index_path,
                    org_id=org_id,
                )
                logger.info("RAG pipeline initialized")
            except Exception as e:
                logger.warning(f"RAG pipeline init failed: {e}")

    @property
    def is_available(self) -> bool:
        return self.pipeline is not None

    def ingest_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """Ingest documents into RAG index."""
        if not self.is_available:
            return {"error": "RAG not available", "documents_ingested": 0}

        try:
            stats = self.pipeline.ingest_and_index(file_paths)
            return stats
        except Exception as e:
            logger.error(f"RAG ingestion failed: {e}")
            return {"error": str(e), "documents_ingested": 0}

    def query(
        self, query: str, top_k: int = 5, min_score: float = 0.0,
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Query RAG for relevant context."""
        if not self.is_available:
            return {"results": [], "error": "RAG not available"}

        try:
            results = self.pipeline.query(
                query=query,
                top_k=top_k,
                min_score=min_score,
                filters=filters,
            )
            return {"results": results, "query": query, "total_results": len(results)}
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return {"results": [], "error": str(e)}

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG index statistics."""
        if not self.is_available:
            return {"status": "unavailable"}
        try:
            return self.pipeline.get_stats()
        except Exception as e:
            return {"status": "error", "error": str(e)}

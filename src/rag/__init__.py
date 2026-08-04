"""
InsightForge AI - RAG Module

Optional module for contextual understanding support.
Retrieves relevant business context for anomaly explanation.
"""

__version__ = "1.0.0"

from .models import (
    Document,
    DocumentChunk,
    RetrievalResult,
    RAGQuery,
    RAGResponse,
)
from .ingestion import DocumentIngester, IngestionConfig
from .chunker import TextChunker, ChunkConfig
from .embeddings import EmbeddingGenerator, EmbeddingConfig
from .vectorstore import FAISSVectorStore
from .retriever import RAGRetriever
from .pipeline import RAGPipeline, create_pipeline

__all__ = [
    # Models
    "Document",
    "DocumentChunk",
    "RetrievalResult",
    "RAGQuery",
    "RAGResponse",
    # Ingestion
    "DocumentIngester",
    "IngestionConfig",
    # Chunking
    "TextChunker",
    "ChunkConfig",
    # Embeddings
    "EmbeddingGenerator",
    "EmbeddingConfig",
    # Vector Store
    "FAISSVectorStore",
    # Retriever
    "RAGRetriever",
    # Pipeline
    "RAGPipeline",
    "create_pipeline",
]

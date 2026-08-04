"""
Retriever module for RAG pipeline.

Orchestrates retrieval: query embedding, vector search, filtering, ranking.
Returns structured results with relevance scores.
"""

import time
import logging
from typing import List, Dict, Any, Optional, Callable
import numpy as np

from .models import Document, DocumentChunk, RAGQuery, RAGResponse, RetrievalResult
from .embeddings import EmbeddingGenerator
from .vectorstore import FAISSVectorStore

logger = logging.getLogger(__name__)


class RAGRetriever:
    """
    High-level retriever that orchestrates the search pipeline.

    Combines:
    - Query embedding generation
    - Vector similarity search
    - Metadata filtering
    - Result ranking and formatting
    """

    def __init__(self, vector_store: FAISSVectorStore,
                 embedding_generator: Optional[EmbeddingGenerator] = None):
        """
        Initialize retriever.

        Args:
            vector_store: Initialized vector store
            embedding_generator: Optional embedding generator (uses store's if None)
        """
        self.vector_store = vector_store
        self.embedding_gen = embedding_generator or vector_store.embedding_gen

    def retrieve(self, query: RAGQuery,
                 load_documents: bool = False) -> RAGResponse:
        """
        Execute a retrieval query.

        Pipeline:
        1. Generate query embedding
        2. Perform vector similarity search
        3. Apply metadata filters
        4. Filter by minimum score
        5. Format results

        Args:
            query: Query parameters
            load_documents: Whether to load full document data for results

        Returns:
            RAGResponse with results

        Raises:
            ValueError: If query invalid or embedding fails
        """
        start_time = time.time()

        try:
            # 1. Generate query embedding
            logger.debug(f"Generating embedding for query: {query.query[:50]}...")
            query_embedding = self.embedding_gen.generate_single(query.query)

            # 2. Define filter function based on query filters
            filter_func = self._build_filter(query.filters) if query.filters else None

            # 3. Perform search
            search_start = time.time()
            raw_results = self.vector_store.search(
                query_embedding,
                k=query.top_k * 2,  # Request more to allow for filtering
                filter_func=filter_func
            )
            search_time = time.time() - search_start

            # 4. Filter by minimum score and limit to top_k
            filtered_results = [
                r for r in raw_results
                if r["similarity_score"] >= query.min_score
            ][:query.top_k]

            # 5. Format results with proper ranks
            retrieval_results = self._format_results(
                filtered_results,
                load_documents=load_documents
            )

            # 6. Build response
            query_time = (time.time() - start_time) * 1000
            response = RAGResponse(
                query=query.query,
                results=retrieval_results,
                total_results=len(raw_results),
                query_time_ms=query_time,
                metadata={
                    "embedding_time_ms": 0,  # Could track separately
                    "search_time_ms": search_time * 1000,
                    "filters_applied": query.filters if query.filters else None,
                    "top_k_requested": query.top_k,
                    "org_id": query.org_id
                }
            )

            logger.info(
                f"Retrieved {len(retrieval_results)} results "
                f"({len(raw_results)} total, {query_time:.1f}ms)"
            )

            return response

        except Exception as e:
            logger.exception(f"Retrieval failed for query: {query.query}")
            raise

    def _build_filter(self, filters: Dict[str, Any]) -> Callable[[Dict], bool]:
        """
        Build a metadata filter function.

        Args:
            filters: Dictionary of metadata key -> expected value(s)

        Returns:
            Filter function that returns True if metadata matches all filters
        """
        def filter_func(metadata: Dict) -> bool:
            for key, expected in filters.items():
                actual = metadata.get(key)

                # Handle list of acceptable values
                if isinstance(expected, list):
                    if actual not in expected:
                        return False
                elif actual != expected:
                    return False

            return True

        return filter_func

    def _format_results(self, raw_results: List[Dict],
                       load_documents: bool = False) -> List[RetrievalResult]:
        """
        Format raw search results into RetrievalResult objects.

        Args:
            raw_results: Raw search results from vector store
            load_documents: Whether to include full document data

        Returns:
            List of RetrievalResult objects
        """
        results = []

        for i, raw in enumerate(raw_results):
            # Build chunk object
            chunk = DocumentChunk(
                id=raw["chunk_id"],
                document_id=raw["document_id"],
                org_id=raw["org_id"],
                chunk_index=0,  # Not stored in metadata, could add if needed
                text=raw["text"],
                metadata=raw["metadata"],
                embedding=None  # Don't return embeddings to save bandwidth
            )

            # Create RetrievalResult
            result = RetrievalResult(
                chunk=chunk,
                similarity_score=raw["similarity_score"],
                rank=i + 1,
                document=None  # Not loaded by default
            )

            results.append(result)

        return results

    def retrieve_with_context(self, query: str, org_id: str, top_k: int = 5,
                             filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Simplified retrieval returning dict format.

        Args:
            query: Query string
            org_id: Organization ID
            top_k: Number of results
            filters: Optional metadata filters

        Returns:
            List of result dictionaries with text, score, and metadata
        """
        query_obj = RAGQuery(
            query=query,
            org_id=org_id,
            top_k=top_k,
            filters=filters or {},
            min_score=0.0
        )

        response = self.retrieve(query_obj, load_documents=False)

        # Convert to simple dict format
        simple_results = []
        for result in response.results:
            simple_results.append({
                "text": result.chunk.text,
                "score": float(result.similarity_score),
                "rank": result.rank,
                "chunk_id": result.chunk.id,
                "document_id": result.chunk.document_id,
                "metadata": result.chunk.metadata
            })

        return simple_results

    def search_similar_to_chunk(self, chunk_id: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Find chunks similar to a specific chunk (by ID).

        Args:
            chunk_id: Source chunk ID
            k: Number of similar chunks

        Returns:
            List of similar chunks with similarity scores
        """
        if chunk_id not in self.vector_store.chunk_id_to_faiss_id:
            logger.warning(f"Chunk ID not found: {chunk_id}")
            return []

        faiss_id = self.vector_store.chunk_id_to_faiss_id[chunk_id]

        # Get embedding from metadata? Not stored there.
        # Would need to reconstruct from index or have separate lookup
        logger.error("Chunk similarity search not implemented without stored embedding")
        return []

    def get_relevant_context(self, anomaly_context: Dict[str, Any],
                            top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Get relevant context based on anomaly metadata.

        Convenience method for root cause/explanation services.

        Args:
            anomaly_context: Dict with anomaly details (metric, dimensions, timestamp, etc.)
            top_k: Number of context chunks

        Returns:
            List of relevant context documents with scores
        """
        # Build query from anomaly context
        query_parts = []

        metric = anomaly_context.get("metric", "")
        if metric:
            query_parts.append(f"metric: {metric}")

        dimensions = anomaly_context.get("dimensions", {})
        for key, value in dimensions.items():
            query_parts.append(f"{key}: {value}")

        anomaly_type = anomaly_context.get("anomaly_type", "")
        if anomaly_type:
            query_parts.append(f"type: {anomaly_type}")

        # Include business question if provided
        question = anomaly_context.get("question", "")
        if question:
            query_parts.append(question)

        query = " ".join(query_parts)

        if not query.strip():
            logger.warning("Empty query from anomaly context")
            return []

        # Build filters: only return docs for this org
        filters = {}
        if "org_id" in anomaly_context:
            filters["org_id"] = anomaly_context["org_id"]

        # Maybe filter by document type based on context?
        # e.g., for metric questions, prefer metric_def or incident docs
        if "document_type" in anomaly_context:
            filters["document_type"] = anomaly_context["document_type"]

        return self.retrieve_with_context(
            query=query,
            org_id=anomaly_context.get("org_id", ""),
            top_k=top_k,
            filters=filters if filters else None
        )


def create_default_retriever(vector_store: Optional[FAISSVectorStore] = None,
                            index_path: Optional[str] = None) -> RAGRetriever:
    """
    Create retriever with default components.

    Args:
        vector_store: Optional existing vector store
        index_path: Path for vector store (creates new if None or not provided)

    Returns:
        Initialized RAGRetriever
    """
    if vector_store is None:
        if index_path:
            vector_store = create_default_vector_store(index_path)
        else:
            # Create in-memory store
            from .embeddings import create_default_embedding_generator
            embedding_gen = create_default_embedding_generator()
            vector_store = FAISSVectorStore(embedding_gen)

    return RAGRetriever(vector_store)

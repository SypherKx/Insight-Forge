"""
Text chunking module for RAG pipeline.

Splits documents into coherent chunks with overlap.
Uses token-based chunking for consistency with embedding models.
"""

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ChunkConfig:
    """Configuration for text chunking."""
    chunk_size: int = 500  # Target tokens per chunk
    overlap: int = 50  # Token overlap between chunks
    min_chunk_size: int = 1  # Minimum chunk size
    max_chunk_size: int = 1000  # Maximum chunk size
    separator: str = "\n"  # Preferred separator for splitting
    keep_separator: bool = False


class TextChunker:
    """
    Splits text into overlapping chunks for embedding.

    Uses a token-aware approach (approximates tokens as words/punctuation).
    Preserves sentence boundaries when possible to maintain coherence.
    """

    def __init__(self, config: Optional[ChunkConfig] = None):
        """
        Initialize chunker.

        Args:
            config: Chunking configuration (uses defaults if None)
        """
        self.config = config or ChunkConfig()
        self._separator_pattern = self._compile_separator_pattern()

    def _compile_separator_pattern(self) -> re.Pattern:
        """Compile regex for splitting on separators."""
        # Split on double newlines, then single newlines, then sentences
        separators = [
            r"\n\s*\n",  # Double newline
            r"\n",  # Single newline
            r"(?<=[.!?])\s+",  # Sentence boundary
            r"(?<=;)\s+",  # Semicolon boundary
            r"\s+",  # Word boundary (fallback)
        ]
        return re.compile("|".join(separators))

    def _count_tokens(self, text: str) -> int:
        """
        Approximate token count.

        Uses a simple heuristic: tokens ≈ words + punctuation.
        For more accuracy, could use tiktoken or transformers tokenizer.

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
        return len(tokens)

    def _split_by_separators(self, text: str) -> List[str]:
        """
        Split text by preferred separators while preserving coherence.

        Args:
            text: Text to split

        Returns:
            List of text segments
        """
        # First try splitting by double newlines (paragraphs)
        segments = re.split(r'\n\s*\n', text)

        # If segments are too large, split further
        result = []
        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue

            token_count = self._count_tokens(segment)

            if token_count <= self.config.chunk_size * 1.5:
                result.append(segment)
            else:
                # Split long segments by single newlines or sentences
                sub_segments = self._separator_pattern.split(segment)
                sub_segments = [s.strip() for s in sub_segments if s.strip()]
                result.extend(sub_segments)

        return result

    def chunk_text(self, text: str, document_id: str, chunk_prefix: str = "") -> List[dict]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            document_id: Source document ID
            chunk_prefix: Prefix to add to each chunk (e.g., document title)

        Returns:
            List of chunk dictionaries with metadata
        """
        if not text or not text.strip():
            logger.warning(f"Empty text provided for document {document_id}")
            return []

        # Clean text
        text = self._clean_text(text)

        # Split into base segments
        segments = self._split_by_separators(text)

        chunks = []
        current_chunk = []
        current_token_count = 0
        chunk_index = 0

        for segment in segments:
            segment_tokens = self._count_tokens(segment)

            # If segment itself is larger than max chunk size, force split
            if segment_tokens > self.config.max_chunk_size:
                logger.warning(f"Segment too large ({segment_tokens} tokens), force splitting")
                # Split the segment by character limit as last resort
                char_limit = self.config.chunk_size * 4  # Approx 4 chars per token
                for i in range(0, len(segment), char_limit):
                    forced_segment = segment[i:i + char_limit]
                    if forced_segment.strip():
                        segments.append(forced_segment)
                continue

            # Would adding this segment exceed the chunk size?
            if current_token_count + segment_tokens > self.config.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = self.config.separator.join(current_chunk)
                if chunk_prefix:
                    chunk_text = f"{chunk_prefix}\n\n{chunk_text}"

                chunks.append({
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "token_count": current_token_count,
                    "segment_count": len(current_chunk)
                })
                chunk_index += 1

                # Start new chunk with overlap: keep some segments
                overlap_tokens = 0
                overlap_segments = []
                for seg in reversed(current_chunk):
                    seg_tokens = self._count_tokens(seg)
                    if overlap_tokens + seg_tokens <= self.config.overlap:
                        overlap_segments.insert(0, seg)
                        overlap_tokens += seg_tokens
                    else:
                        break

                current_chunk = overlap_segments
                current_token_count = overlap_tokens

            # Add current segment
            current_chunk.append(segment)
            current_token_count += segment_tokens

        # Don't forget the last chunk
        if current_chunk:
            chunk_text = self.config.separator.join(current_chunk)
            if chunk_prefix:
                chunk_text = f"{chunk_prefix}\n\n{chunk_text}"

            chunks.append({
                "chunk_index": chunk_index,
                "text": chunk_text,
                "token_count": current_token_count,
                "segment_count": len(current_chunk)
            })

        # Filter out chunks that are too small
        chunks = [
            c for c in chunks
            if self.config.min_chunk_size <= c["token_count"] <= self.config.max_chunk_size
        ]

        # Add document_id and final IDs
        for i, chunk in enumerate(chunks):
            chunk["document_id"] = document_id
            chunk["chunk_id"] = f"{document_id}_chunk_{i}"

        logger.info(f"Chunked document {document_id}: {len(chunks)} chunks from {len(text)} chars")
        return chunks

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Normalize whitespace
        text = re.sub(r'\r\n', '\n', text)  # Windows line endings
        text = re.sub(r'\r', '\n', text)  # Old Mac line endings
        text = re.sub(r'\n{3,}', '\n\n', text)  # Multiple blank lines
        text = re.sub(r' {2,}', ' ', text)  # Multiple spaces

        # Remove zero-width characters
        text = re.sub(r'\u200b|\u200c|\u200d|\ufe0f', '', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def chunk_documents(self, documents: List[dict], text_key: str = "content") -> List[dict]:
        """
        Chunk multiple documents.

        Args:
            documents: List of document dicts with at least 'id' and text content
            text_key: Key containing text content in each document

        Returns:
            Flat list of all chunks from all documents
        """
        all_chunks = []

        for doc in documents:
            doc_id = doc.get("id", "unknown")
            title = doc.get("title", "")
            source_path = doc.get("source_path", "")
            doc_meta = doc.get("metadata", {})
            prefix = f"Title: {title}" if title else ""

            text = doc.get(text_key, "")
            if not text:
                logger.warning(f"Document {doc_id} has no text content")
                continue

            chunks = self.chunk_text(text, doc_id, prefix)
            for c in chunks:
                c["title"] = title
                c["source_path"] = source_path
                c["doc_metadata"] = doc_meta
            all_chunks.extend(chunks)

        logger.info(f"Total: {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks


def create_default_chunker() -> TextChunker:
    """Create a chunker with default configuration."""
    config = ChunkConfig(
        chunk_size=500,
        overlap=50,
        min_chunk_size=1,
        max_chunk_size=1000
    )
    return TextChunker(config)

"""
Document ingestion module for RAG pipeline.

Handles loading and extracting text from various file formats:
- PDF (.pdf)
- Plain text (.txt)
- Markdown (.md)
- Future: DOCX, HTML, etc.
"""

import os
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import logging

from .models import Document

logger = logging.getLogger(__name__)


@dataclass
class IngestionConfig:
    """Configuration for document ingestion."""
    allowed_extensions: List[str] = None
    max_file_size_mb: int = 50
    recursive: bool = False  # Recursively scan directories
    encoding: str = "utf-8"

    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = [".pdf", ".txt", ".md"]


class DocumentIngester:
    """
    Handles document loading and text extraction.

    Supports multiple file formats with proper error handling.
    Extracts text content and basic metadata.
    """

    def __init__(self, config: Optional[IngestionConfig] = None):
        """
        Initialize document ingester.

        Args:
            config: Ingestion configuration
        """
        self.config = config or IngestionConfig()
        self._loaded_extractors = self._init_extractors()

    def _init_extractors(self) -> Dict[str, callable]:
        """Initialize file format extractors."""
        return {
            ".pdf": self._extract_pdf,
            ".txt": self._extract_txt,
            ".md": self._extract_markdown,
        }

    def ingest_file(self, file_path: Union[str, Path], org_id: str,
                    document_type: Optional[str] = None) -> Optional[Document]:
        """
        Ingest a single file.

        Args:
            file_path: Path to file
            org_id: Organization ID for multi-tenancy
            document_type: Type classification (auto-detected if None)

        Returns:
            Document object or None if failed
        """
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        # Check file extension
        ext = file_path.suffix.lower()
        if ext not in self.config.allowed_extensions:
            logger.warning(f"Unsupported file type: {ext} for {file_path}")
            return None

        # Check file size
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > self.config.max_file_size_mb:
            logger.error(f"File too large: {size_mb:.1f}MB > {self.config.max_file_size_mb}MB")
            return None

        # Auto-detect document type from path or filename if not provided
        if document_type is None:
            document_type = self._detect_document_type(file_path)

        try:
            # Extract text based on file type
            if ext in self._loaded_extractors:
                content, metadata = self._loaded_extractors[ext](file_path)
            else:
                logger.error(f"No extractor for extension: {ext}")
                return None

            if not content or not content.strip():
                logger.warning(f"No content extracted from {file_path}")
                return None

            # Create Document object
            doc = Document(
                id=str(uuid.uuid4()),
                org_id=org_id,
                title=file_path.stem,
                source_path=str(file_path),
                document_type=document_type,
                content=content,
                metadata={
                    **metadata,
                    "file_size_bytes": file_path.stat().st_size,
                    "file_extension": ext,
                    "file_name": file_path.name,
                },
                created_at=None  # Will be set by pydantic default
            )

            logger.info(f"Ingested {file_path} ({len(content)} chars, {metadata.get('page_count', 0)} pages)")
            return doc

        except Exception as e:
            logger.exception(f"Failed to ingest {file_path}: {e}")
            return None

    def ingest_directory(self, directory_path: Union[str, Path], org_id: str,
                         document_type: Optional[str] = None) -> List[Document]:
        """
        Ingest all supported files in a directory.

        Args:
            directory_path: Directory to scan
            org_id: Organization ID
            document_type: Override document type (auto-detected per file if None)

        Returns:
            List of successfully ingested documents
        """
        directory_path = Path(directory_path)

        if not directory_path.is_dir():
            logger.error(f"Not a directory: {directory_path}")
            return []

        documents = []
        pattern = "**/*" if self.config.recursive else "*"

        for file_path in directory_path.glob(pattern):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in self.config.allowed_extensions:
                    doc = self.ingest_file(file_path, org_id, document_type)
                    if doc:
                        documents.append(doc)

        logger.info(f"Ingested {len(documents)} documents from {directory_path}")
        return documents

    def _detect_document_type(self, file_path: Path) -> str:
        """
        Detect document type from filename or path.

        Args:
            file_path: File path

        Returns:
            Document type string
        """
        name = file_path.stem.lower()

        # Check for known keywords in filename
        type_mappings = {
            "metric": "metric_def",
            "definition": "metric_def",
            "glossary": "metric_def",
            "process": "process",
            "procedure": "process",
            "runbook": "process",
            "incident": "incident",
            "postmortem": "incident",
            "outage": "incident",
            "issue": "incident",
        }

        for keyword, doc_type in type_mappings.items():
            if keyword in name:
                return doc_type

        # Check directory path
        parent = file_path.parent.name.lower()
        if "process" in parent or "procedure" in parent:
            return "process"
        if "incident" in parent or "postmortem" in parent:
            return "incident"
        if "metric" in parent or "definition" in parent:
            return "metric_def"

        # Default
        return "other"

    def _extract_pdf(self, file_path: Path) -> tuple[str, dict]:
        """
        Extract text from PDF file.

        Args:
            file_path: PDF file path

        Returns:
            Tuple: (text_content, metadata)
        """
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(file_path))
            pages = []

            metadata = {
                "page_count": len(reader.pages),
                "author": reader.metadata.author if reader.metadata else None,
                "title": reader.metadata.title if reader.metadata else None,
                "creation_date": str(reader.metadata.creation_date) if reader.metadata else None,
            }

            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        pages.append(page_text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {i} of {file_path}: {e}")

            content = "\n\n".join(pages)
            return content, metadata

        except ImportError:
            logger.error("pypdf not installed. Install with: pip install pypdf")
            raise
        except Exception as e:
            logger.exception(f"PDF extraction failed for {file_path}")
            raise

    def _extract_txt(self, file_path: Path) -> tuple[str, dict]:
        """
        Extract text from plain text file.

        Args:
            file_path: Text file path

        Returns:
            Tuple: (text_content, metadata)
        """
        try:
            with open(file_path, 'r', encoding=self.config.encoding) as f:
                content = f.read()

            metadata = {
                "file_size": file_path.stat().st_size,
                "encoding": self.config.encoding,
            }

            return content, metadata

        except UnicodeDecodeError:
            # Try with different encodings
            for encoding in ['utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    metadata = {"encoding": encoding}
                    return content, metadata
                except UnicodeDecodeError:
                    continue

            logger.error(f"Unable to decode text file: {file_path}")
            raise

    def _extract_markdown(self, file_path: Path) -> tuple[str, dict]:
        """
        Extract text from Markdown file.

        Args:
            file_path: Markdown file path

        Returns:
            Tuple: (text_content, metadata)
        """
        # Markdown is plain text with formatting
        content, metadata = self._extract_txt(file_path)
        metadata["file_type"] = "markdown"
        return content, metadata


def create_default_ingester() -> DocumentIngester:
    """Create ingester with default configuration."""
    config = IngestionConfig(
        allowed_extensions=[".pdf", ".txt", ".md"],
        max_file_size_mb=50,
        recursive=False
    )
    return DocumentIngester(config)

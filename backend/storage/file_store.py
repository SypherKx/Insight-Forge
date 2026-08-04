"""
Local file storage for uploaded CSV files.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FileStore:
    """Manages uploaded file storage on local filesystem."""

    def __init__(self, upload_dir: str = "./uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(self, file_content: bytes, dataset_id: str, filename: str) -> str:
        """
        Save uploaded file to storage.

        Args:
            file_content: Raw file bytes
            dataset_id: Dataset ID for directory organization
            filename: Original filename

        Returns:
            Storage path
        """
        dataset_dir = self.upload_dir / dataset_id
        dataset_dir.mkdir(parents=True, exist_ok=True)

        file_path = dataset_dir / filename
        with open(file_path, "wb") as f:
            f.write(file_content)

        logger.info(f"Saved upload: {file_path} ({len(file_content)} bytes)")
        return str(file_path)

    def get_file_path(self, dataset_id: str, filename: str) -> Optional[Path]:
        """Get path to stored file."""
        file_path = self.upload_dir / dataset_id / filename
        if file_path.exists():
            return file_path
        return None

    def delete_dataset_files(self, dataset_id: str):
        """Delete all files for a dataset."""
        dataset_dir = self.upload_dir / dataset_id
        if dataset_dir.exists():
            shutil.rmtree(dataset_dir)
            logger.info(f"Deleted files for dataset {dataset_id}")

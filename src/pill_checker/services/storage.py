"""Storage service for handling file operations."""

import os
import uuid
from pathlib import Path
from typing import BinaryIO, Optional

import aiofiles

from pill_checker.core.config import settings
from pill_checker.core.logging_config import logger


class StorageService:
    """Service for handling file storage operations on local filesystem."""

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize storage service.

        Args:
            base_path: Base directory for file storage. Defaults to ./storage
        """
        self.base_path = Path(base_path or os.getenv("STORAGE_PATH", "./storage"))
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Storage service initialized with base path: {self.base_path}")

    async def upload_file(
        self,
        file_content: bytes,
        file_path: str,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Upload a file to local storage.

        Args:
            file_content: File content as bytes
            file_path: Relative path where file should be stored
            content_type: MIME type of the file (optional, for metadata)

        Returns:
            str: Public URL/path to access the file

        Raises:
            Exception: If upload fails
        """
        try:
            full_path = self.base_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file asynchronously
            async with aiofiles.open(full_path, "wb") as f:
                await f.write(file_content)

            logger.info(f"File uploaded successfully to {file_path}")

            # Return relative path that can be served by the application
            return f"/storage/{file_path}"

        except Exception as e:
            logger.error(f"Failed to upload file to {file_path}: {e}")
            raise

    async def download_file(self, file_path: str) -> Optional[bytes]:
        """
        Download a file from local storage.

        Args:
            file_path: Relative path of the file to download

        Returns:
            bytes: File content, or None if file doesn't exist
        """
        try:
            full_path = self.base_path / file_path

            if not full_path.exists():
                logger.warning(f"File not found: {file_path}")
                return None

            async with aiofiles.open(full_path, "rb") as f:
                content = await f.read()

            return content

        except Exception as e:
            logger.error(f"Failed to download file from {file_path}: {e}")
            return None

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from local storage.

        Args:
            file_path: Relative path of the file to delete

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            full_path = self.base_path / file_path

            if full_path.exists():
                full_path.unlink()
                logger.info(f"File deleted successfully: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False

    def get_public_url(self, file_path: str) -> str:
        """
        Get public URL for a file.

        Args:
            file_path: Relative path of the file

        Returns:
            str: Public URL to access the file
        """
        return f"/storage/{file_path}"


# Singleton instance
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get or create storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service

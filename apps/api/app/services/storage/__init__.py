import os
import shutil
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from app.config import settings


class StorageProvider(ABC):
    @abstractmethod
    def upload(self, file_obj: BinaryIO, storage_key: str) -> str:
        """Upload a file to storage and return the storage key/URI."""
        pass

    @abstractmethod
    def download(self, storage_key: str) -> bytes:
        """Download a file by storage key."""
        pass

    @abstractmethod
    def delete(self, storage_key: str) -> bool:
        """Delete a file by storage key."""
        pass

    @abstractmethod
    def get_path_or_url(self, storage_key: str) -> str:
        """Get local path or signed URL."""
        pass


class LocalStorageProvider(StorageProvider):
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or settings.STORAGE_DIR
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_full_path(self, storage_key: str) -> str:
        # Sanitize storage key to avoid path traversal
        clean_key = os.path.normpath(storage_key).lstrip(r"\/")
        full_path = os.path.join(self.base_dir, clean_key)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        return full_path

    def upload(self, file_obj: BinaryIO, storage_key: str) -> str:
        full_path = self._get_full_path(storage_key)
        file_obj.seek(0)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(file_obj, f)
        return storage_key

    def download(self, storage_key: str) -> bytes:
        full_path = self._get_full_path(storage_key)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {storage_key}")
        with open(full_path, "rb") as f:
            return f.read()

    def delete(self, storage_key: str) -> bool:
        full_path = self._get_full_path(storage_key)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False

    def get_path_or_url(self, storage_key: str) -> str:
        return self._get_full_path(storage_key)


def get_storage_provider() -> StorageProvider:
    if settings.STORAGE_PROVIDER == "local" or not settings.STORAGE_BUCKET:
        return LocalStorageProvider()
    # Default to LocalStorageProvider for dev / portable setups
    return LocalStorageProvider()

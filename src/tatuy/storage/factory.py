"""Storage provider composition helpers."""

from __future__ import annotations

from pathlib import Path

from tatuy.storage.contracts import StorageProvider
from tatuy.storage.ephemeral import EphemeralStorageProvider
from tatuy.storage.filesystem import FilesystemStorageProvider


def create_storage_provider(
    provider: str = "filesystem",
    *,
    root: str | Path = ".tatuy/storage",
) -> StorageProvider:
    """Create one configured logical storage provider."""
    if provider == "filesystem":
        return FilesystemStorageProvider(root)
    if provider == "ephemeral":
        return EphemeralStorageProvider()
    raise ValueError(f"Unknown storage provider: {provider}")

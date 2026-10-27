"""Logical application storage providers."""

from tatuy.storage.contracts import StorageProvider
from tatuy.storage.ephemeral import EphemeralStorageProvider
from tatuy.storage.filesystem import FilesystemStorageProvider

__all__ = [
    "EphemeralStorageProvider",
    "FilesystemStorageProvider",
    "StorageProvider",
]

"""Runtime-facing logical storage contract."""

from __future__ import annotations

from typing import Protocol


class StorageProvider(Protocol):
    """Read and write application data through host-independent logical keys."""

    @property
    def persistent(self) -> bool:
        """Whether data is expected to survive the current runtime session."""

    def exists(self, key: str) -> bool:
        """Return whether a logical storage key exists."""

    def read_bytes(self, key: str) -> bytes:
        """Read bytes stored at one logical key."""

    def write_bytes(self, key: str, data: bytes) -> None:
        """Write bytes to one logical key."""

    def read_text(self, key: str, *, encoding: str = "utf-8") -> str:
        """Read text stored at one logical key."""

    def write_text(
        self,
        key: str,
        text: str,
        *,
        encoding: str = "utf-8",
    ) -> None:
        """Write text to one logical key."""

    def delete(self, key: str) -> None:
        """Delete one logical storage key when it exists."""

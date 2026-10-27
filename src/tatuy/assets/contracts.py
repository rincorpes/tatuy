"""Logical asset access contracts used by runtime and gameplay code."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, Protocol, TextIO


class AssetProvider(Protocol):
    """Resolve read-only logical assets without exposing host-specific locations."""

    def path(self, asset: str) -> Path:
        """Return the resolved path for one existing logical asset."""

    def exists(self, asset: str) -> bool:
        """Return whether one logical asset exists."""

    def open_binary(self, asset: str) -> BinaryIO:
        """Open one logical asset for binary reading."""

    def open_text(self, asset: str, *, encoding: str = "utf-8") -> TextIO:
        """Open one logical asset for text reading."""

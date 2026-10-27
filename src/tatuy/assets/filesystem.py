"""Filesystem-backed logical asset provider."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, TextIO


class FilesystemAssetProvider:
    """Resolve logical asset names beneath one read-only filesystem root."""

    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root).expanduser().resolve()

    @classmethod
    def from_file(
        cls,
        filename: str | Path,
        root: str | Path = ".",
    ) -> FilesystemAssetProvider:
        """Create a provider rooted relative to a Python module or target file."""
        return cls(Path(filename).resolve().parent / root)

    def _resolve(self, asset: str) -> Path:
        logical = Path(asset)
        if logical.is_absolute():
            raise ValueError("Asset names must be relative")

        resolved = (self.root / logical).resolve()
        if not resolved.is_relative_to(self.root):
            raise ValueError(
                f"Asset {asset!r} escapes the configured asset root"
            )
        return resolved

    def path(self, asset: str) -> Path:
        """Return the resolved path for one existing logical asset."""
        resolved = self._resolve(asset)
        if not resolved.is_file():
            raise FileNotFoundError(str(resolved))
        return resolved

    def exists(self, asset: str) -> bool:
        """Return whether one logical asset exists below the configured root."""
        try:
            return self._resolve(asset).is_file()
        except ValueError:
            return False

    def open_binary(self, asset: str) -> BinaryIO:
        """Open one logical asset for binary reading."""
        return self.path(asset).open("rb")

    def open_text(self, asset: str, *, encoding: str = "utf-8") -> TextIO:
        """Open one logical asset for text reading."""
        return self.path(asset).open("r", encoding=encoding)

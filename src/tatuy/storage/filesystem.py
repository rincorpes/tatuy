"""Filesystem-backed logical storage provider."""

from __future__ import annotations

from pathlib import Path

from tatuy.storage.keys import normalize_storage_key


class FilesystemStorageProvider:
    """Persist logical storage keys beneath one configured filesystem root."""

    def __init__(self, root: str | Path = ".tatuy/storage") -> None:
        self.root = Path(root).expanduser().resolve()

    @property
    def persistent(self) -> bool:
        return True

    def _path(self, key: str) -> Path:
        logical_key = normalize_storage_key(key)
        path = (self.root / logical_key).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("Storage key escapes the configured storage root")
        return path

    def exists(self, key: str) -> bool:
        return self._path(key).is_file()

    def read_bytes(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def write_bytes(self, key: str, data: bytes) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def read_text(self, key: str, *, encoding: str = "utf-8") -> str:
        return self._path(key).read_text(encoding=encoding)

    def write_text(
        self,
        key: str,
        text: str,
        *,
        encoding: str = "utf-8",
    ) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding=encoding)

    def delete(self, key: str) -> None:
        path = self._path(key)
        if path.is_file():
            path.unlink()

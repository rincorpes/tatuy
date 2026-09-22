from __future__ import annotations

from pathlib import Path


class FileService:
    """Adapter for local file operations."""

    @classmethod
    def write_text(cls, path: str, text: str):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch()
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    @classmethod
    def write_bytes(cls, path: str, data: bytes):
        with open(path, "wb") as f:
            f.write(data)
            f.write(data)

    @classmethod
    def validate_file_exists(cls, path: str) -> str:
        """
        Validate that a file exists at the given path.
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(str(p))
        return str(p)

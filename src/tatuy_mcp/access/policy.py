from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AccessPolicy:
    blocked_directories: frozenset[str]
    blocked_filenames: frozenset[str]
    blocked_extensions: frozenset[str]
    searchable_extensions: frozenset[str]
    writable_extensions: frozenset[str]
    writable_filenames: frozenset[str]

    def check_access(self, relative_path: Path) -> None:
        parts = [part.casefold() for part in relative_path.parts]
        if any(part in self.blocked_directories for part in parts):
            raise ValueError("Path belongs to an excluded directory")

        name = relative_path.name.casefold()
        if name.startswith(".env") or name in self.blocked_filenames:
            raise ValueError("File is excluded from project access")

        if relative_path.suffix.casefold() in self.blocked_extensions:
            raise ValueError("File type is excluded from project access")

    def check_writable_file(self, path: Path) -> None:
        if (
            path.suffix.casefold() not in self.writable_extensions
            and path.name not in self.writable_filenames
        ):
            raise ValueError(
                f"File type is not writable through MCP: {path.name}"
            )

    def is_searchable(self, path: Path) -> bool:
        if path.name.casefold().startswith(".env"):
            return False
        return path.suffix.casefold() in self.searchable_extensions


DEFAULT_ACCESS_POLICY = AccessPolicy(
    blocked_directories=frozenset(
        {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            "node_modules",
            "build",
            "dist",
        }
    ),
    blocked_filenames=frozenset({"credentials.json", "secrets.json"}),
    blocked_extensions=frozenset({".pem", ".key", ".p12", ".pfx"}),
    searchable_extensions=frozenset(
        {
            ".py",
            ".toml",
            ".md",
            ".json",
            ".yaml",
            ".yml",
            ".txt",
            ".glsl",
            ".vert",
            ".frag",
        }
    ),
    writable_extensions=frozenset(
        {
            ".py",
            ".toml",
            ".md",
            ".json",
            ".yaml",
            ".yml",
            ".txt",
            ".glsl",
            ".vert",
            ".frag",
        }
    ),
    writable_filenames=frozenset({".gitignore"}),
)

"""Validation helpers for logical storage keys."""

from __future__ import annotations


def normalize_storage_key(key: str) -> str:
    """Normalize a relative logical key and reject host-path escapes."""
    normalized = key.replace("\\", "/")
    if not normalized or normalized.startswith("/"):
        raise ValueError("Storage keys must be non-empty relative paths")

    parts = [part for part in normalized.split("/") if part not in {"", "."}]
    if not parts or any(part == ".." for part in parts):
        raise ValueError("Storage keys cannot escape the storage root")
    if len(parts[0]) >= 2 and parts[0][1] == ":":
        raise ValueError("Storage keys cannot use absolute drive paths")

    return "/".join(parts)

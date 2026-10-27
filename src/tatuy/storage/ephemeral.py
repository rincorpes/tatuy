"""In-memory storage provider for non-persistent hosts."""

from __future__ import annotations

from tatuy.storage.keys import normalize_storage_key


class EphemeralStorageProvider:
    """Store logical keys in memory for the lifetime of one runtime session."""

    def __init__(self) -> None:
        self._data: dict[str, bytes] = {}

    @property
    def persistent(self) -> bool:
        return False

    def exists(self, key: str) -> bool:
        return normalize_storage_key(key) in self._data

    def read_bytes(self, key: str) -> bytes:
        logical_key = normalize_storage_key(key)
        try:
            return self._data[logical_key]
        except KeyError as exc:
            raise FileNotFoundError(logical_key) from exc

    def write_bytes(self, key: str, data: bytes) -> None:
        self._data[normalize_storage_key(key)] = bytes(data)

    def read_text(self, key: str, *, encoding: str = "utf-8") -> str:
        return self.read_bytes(key).decode(encoding)

    def write_text(
        self,
        key: str,
        text: str,
        *,
        encoding: str = "utf-8",
    ) -> None:
        self.write_bytes(key, text.encode(encoding))

    def delete(self, key: str) -> None:
        self._data.pop(normalize_storage_key(key), None)

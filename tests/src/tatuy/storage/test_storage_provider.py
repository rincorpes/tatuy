"""Logical storage providers isolate game-facing persistence from host paths."""

from pathlib import Path

import pytest

from tatuy.storage.ephemeral import EphemeralStorageProvider
from tatuy.storage.filesystem import FilesystemStorageProvider
from tatuy.storage.keys import normalize_storage_key


def test_filesystem_storage_round_trip_is_scoped_to_root(tmp_path: Path) -> None:
    provider = FilesystemStorageProvider(tmp_path)

    provider.write_text("saves/slot-1.json", '{"level": 3}')

    assert provider.persistent is True
    assert provider.exists("saves/slot-1.json") is True
    assert provider.read_text("saves/slot-1.json") == '{"level": 3}'
    assert (tmp_path / "saves" / "slot-1.json").exists()

    provider.delete("saves/slot-1.json")
    assert provider.exists("saves/slot-1.json") is False


def test_ephemeral_storage_round_trip_does_not_touch_filesystem() -> None:
    provider = EphemeralStorageProvider()

    provider.write_bytes("state/checkpoint.bin", b"tatuy")

    assert provider.persistent is False
    assert provider.exists("state/checkpoint.bin") is True
    assert provider.read_bytes("state/checkpoint.bin") == b"tatuy"

    provider.delete("state/checkpoint.bin")
    assert provider.exists("state/checkpoint.bin") is False


def test_ephemeral_missing_key_raises_file_not_found() -> None:
    provider = EphemeralStorageProvider()

    with pytest.raises(FileNotFoundError):
        provider.read_bytes("missing.bin")


@pytest.mark.parametrize(
    "key",
    ["../outside.txt", "/absolute.txt", "C:/absolute.txt", "C:\\absolute.txt"],
)
def test_storage_keys_reject_absolute_or_parent_escape(key: str) -> None:
    with pytest.raises(ValueError):
        normalize_storage_key(key)


def test_storage_keys_normalize_host_separators() -> None:
    assert normalize_storage_key("saves\\slot.json") == "saves/slot.json"

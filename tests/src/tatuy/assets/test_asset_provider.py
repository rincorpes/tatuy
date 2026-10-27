"""Filesystem asset providers keep logical reads inside one configured root."""

from pathlib import Path

import pytest

from tatuy.assets import FilesystemAssetProvider


def test_filesystem_provider_resolves_and_reads_logical_assets(
    tmp_path: Path,
) -> None:
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "data.bin").write_bytes(b"tatuy")
    (assets / "message.txt").write_text("hello", encoding="utf-8")
    provider = FilesystemAssetProvider(tmp_path)

    assert provider.exists("assets/data.bin") is True
    assert provider.path("assets/data.bin") == (assets / "data.bin").resolve()
    with provider.open_binary("assets/data.bin") as stream:
        assert stream.read() == b"tatuy"
    with provider.open_text("assets/message.txt") as stream:
        assert stream.read() == "hello"


def test_filesystem_provider_rejects_absolute_and_parent_escape(
    tmp_path: Path,
) -> None:
    provider = FilesystemAssetProvider(tmp_path)

    with pytest.raises(ValueError, match="relative"):
        provider.path(str((tmp_path / "asset.bin").resolve()))
    with pytest.raises(ValueError, match="escapes"):
        provider.path("../outside.bin")
    assert provider.exists("../outside.bin") is False


def test_filesystem_provider_from_file_roots_relative_to_target_file(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    shared = tmp_path / "shared"
    target.mkdir()
    shared.mkdir()
    app_file = target / "app.py"
    app_file.write_text("", encoding="utf-8")
    (shared / "asset.txt").write_text("asset", encoding="utf-8")

    provider = FilesystemAssetProvider.from_file(app_file, "../shared")

    assert provider.path("asset.txt") == (shared / "asset.txt").resolve()

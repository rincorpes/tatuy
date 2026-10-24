"""Tests for the temporary Tatuy web-spike staging helper."""

from __future__ import annotations

from pathlib import Path

from scripts import prepare_web_spike


def test_prepare_bundles_tatuy_and_pure_python_dependencies(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Build a cache-safe staging tree with Tatuy and its vendored dependency."""
    source_target = tmp_path / "source"
    tatuy_source = tmp_path / "tatuy-source"
    staging_base = tmp_path / "staging"

    source_target.mkdir()
    tatuy_source.mkdir()
    (source_target / "main.py").write_text("print('web')\n", encoding="utf-8")
    (tatuy_source / "__init__.py").write_text("", encoding="utf-8")

    legacy_root = staging_base / source_target.name
    legacy_root.mkdir(parents=True)
    (legacy_root / "stale.txt").write_text("stale", encoding="utf-8")

    monkeypatch.setattr(prepare_web_spike, "SOURCE_TARGET", source_target)
    monkeypatch.setattr(prepare_web_spike, "TATUY_SOURCE", tatuy_source)
    monkeypatch.setattr(prepare_web_spike, "STAGING_BASE", staging_base)

    result = prepare_web_spike.prepare()

    assert result.parent == staging_base
    assert result.name.startswith(f"{source_target.name}-")
    assert (result / "main.py").read_text(encoding="utf-8") == "print('web')\n"
    assert (result / "tatuy" / "__init__.py").exists()
    assert (result / "onomasticon" / "__init__.py").exists()
    assert not legacy_root.exists()


def test_prepare_changes_archive_identity_when_source_changes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Use a new staged folder name whenever packaged source content changes."""
    source_target = tmp_path / "source"
    tatuy_source = tmp_path / "tatuy-source"
    staging_base = tmp_path / "staging"
    source_target.mkdir()
    tatuy_source.mkdir()
    main_file = source_target / "main.py"
    main_file.write_text("print('one')\n", encoding="utf-8")
    (tatuy_source / "__init__.py").write_text("", encoding="utf-8")

    monkeypatch.setattr(prepare_web_spike, "SOURCE_TARGET", source_target)
    monkeypatch.setattr(prepare_web_spike, "TATUY_SOURCE", tatuy_source)
    monkeypatch.setattr(prepare_web_spike, "STAGING_BASE", staging_base)

    first = prepare_web_spike.prepare()
    first_name = first.name
    main_file.write_text("print('two')\n", encoding="utf-8")
    second = prepare_web_spike.prepare()

    assert second.name != first_name
    assert not first.exists()


def test_browser_urls_include_build_identity() -> None:
    """Bust the root HTML cache with the staged content fingerprint."""
    staging = Path(".tatuy/web-spike/001_render_queue-551fc8d2")

    normal, interactive = prepare_web_spike.browser_urls(staging, port=8766)

    assert normal == (
        "http://localhost:8766/index.html?"
        "PYGPI=http://localhost:8766/cdn/&TATUY_BUILD=551fc8d2#"
    )
    assert interactive == (
        "http://localhost:8766/index.html?"
        "PYGPI=http://localhost:8766/cdn/&TATUY_BUILD=551fc8d2&-i#"
    )

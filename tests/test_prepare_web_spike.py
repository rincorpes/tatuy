"""Tests for the temporary Tatuy web-spike staging helper."""

from __future__ import annotations

from pathlib import Path

from scripts import prepare_web_spike


def _configure_target(tmp_path: Path, monkeypatch):
    source_target = tmp_path / "source"
    tatuy_source = tmp_path / "tatuy-source"
    staging_base = tmp_path / "staging"
    source_target.mkdir()
    tatuy_source.mkdir()
    (source_target / "app.py").write_text("def create_app(config): ...\n", encoding="utf-8")
    (source_target / "tatuy.yml").write_text("# defaults\n", encoding="utf-8")
    (source_target / "tatuy.web.yml").write_text(
        "app:\n  loop: asyncio\ncapabilities:\n  capture: false\n",
        encoding="utf-8",
    )
    (tatuy_source / "__init__.py").write_text("", encoding="utf-8")

    monkeypatch.setattr(prepare_web_spike, "SOURCE_TARGET", source_target)
    monkeypatch.setattr(prepare_web_spike, "TATUY_SOURCE", tatuy_source)
    monkeypatch.setattr(prepare_web_spike, "STAGING_BASE", staging_base)
    monkeypatch.setattr(
        prepare_web_spike.ConfigurationLoader,
        "load_profile",
        lambda path, profile: {
            "app": {"loop": "asyncio"},
            "capabilities": {"capture": False},
        },
    )
    return source_target, tatuy_source, staging_base


def test_prepare_bundles_canonical_target_tatuy_and_dependencies(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Build a web staging tree around the canonical target entrypoint."""
    source_target, _, staging_base = _configure_target(tmp_path, monkeypatch)

    legacy_root = staging_base / source_target.name
    legacy_root.mkdir(parents=True)
    (legacy_root / "stale.txt").write_text("stale", encoding="utf-8")

    result = prepare_web_spike.prepare()

    launcher = (result / "main.py").read_text(encoding="utf-8")
    assert result.parent == staging_base
    assert result.name.startswith(f"{source_target.name}-")
    assert "from app import create_app" in launcher
    assert "from tatuy.engine.runtime.host import AsyncRuntimeHost" in launcher
    assert "'loop': 'asyncio'" in launcher
    assert "'capture': False" in launcher
    assert "'replay': False" in launcher
    assert "'audio': {'enabled': False, 'auto_init': False}" in launcher
    assert (result / "app.py").exists()
    assert (result / "tatuy" / "__init__.py").exists()
    assert (result / "onomasticon" / "__init__.py").exists()
    assert not legacy_root.exists()


def test_prepare_changes_archive_identity_when_target_source_changes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Use a new staged folder name whenever canonical target content changes."""
    source_target, _, _ = _configure_target(tmp_path, monkeypatch)
    app_file = source_target / "app.py"

    first = prepare_web_spike.prepare()
    first_name = first.name
    app_file.write_text("def create_app(config): return config\n", encoding="utf-8")
    second = prepare_web_spike.prepare()

    assert second.name != first_name
    assert not first.exists()


def test_browser_launcher_uses_generated_config_and_async_host() -> None:
    launcher = prepare_web_spike._browser_launcher(
        {
            "app": {"loop": "asyncio"},
            "capabilities": {"capture": False},
        }
    )

    assert "import pygame" in launcher
    assert "create_app(WEB_CONFIG)" in launcher
    assert "await AsyncRuntimeHost().run(app.build())" in launcher


def test_browser_urls_include_build_identity() -> None:
    """Bust the root HTML cache with the staged content fingerprint."""
    staging = Path(".tatuy/web-spike/002_render_queue-551fc8d2")

    normal, interactive = prepare_web_spike.browser_urls(staging, port=8766)

    assert normal == (
        "http://localhost:8766/index.html?"
        "PYGPI=http://localhost:8766/cdn/&TATUY_BUILD=551fc8d2#"
    )
    assert interactive == (
        "http://localhost:8766/index.html?"
        "PYGPI=http://localhost:8766/cdn/&TATUY_BUILD=551fc8d2&-i#"
    )

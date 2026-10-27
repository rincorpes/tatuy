"""Tests for the GitHub Pages-style Tatuy web-spike harness."""

from __future__ import annotations

from pathlib import Path

import pytest
from scripts import prepare_web_pages_spike


def test_prepare_pages_site_mounts_build_under_project_subpath(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Copy static Pygbag output under /tatuy and disable Jekyll processing."""
    web_spike_root = tmp_path / "web-spike"
    pages_root = tmp_path / "web-pages"
    staging = web_spike_root / "001_render_queue-551fc8d2"
    build_root = staging / "build" / "web"
    build_root.mkdir(parents=True)
    (build_root / "index.html").write_text("<html></html>\n", encoding="utf-8")
    (build_root / "app.tar.gz").write_bytes(b"archive")

    monkeypatch.setattr(
        prepare_web_pages_spike, "WEB_SPIKE_ROOT", web_spike_root
    )
    monkeypatch.setattr(prepare_web_pages_spike, "PAGES_ROOT", pages_root)

    result = prepare_web_pages_spike.prepare_pages_site(staging)

    assert result == pages_root
    assert (pages_root / ".nojekyll").exists()
    assert (pages_root / "tatuy" / "index.html").exists()
    assert (pages_root / "tatuy" / "app.tar.gz").read_bytes() == b"archive"


def test_prepare_pages_site_requires_static_pygbag_build(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Fail clearly when pygbag has not produced build/web yet."""
    web_spike_root = tmp_path / "web-spike"
    staging = web_spike_root / "001_render_queue-551fc8d2"
    staging.mkdir(parents=True)

    monkeypatch.setattr(
        prepare_web_pages_spike, "WEB_SPIKE_ROOT", web_spike_root
    )

    with pytest.raises(FileNotFoundError, match="Run pygbag with --build"):
        prepare_web_pages_spike.prepare_pages_site(staging)


def test_prepare_pages_site_rejects_paths_outside_web_spike(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Keep cleanup/copy operations constrained to Tatuy's ignored workspace."""
    web_spike_root = tmp_path / "web-spike"
    outside = tmp_path / "outside"
    outside.mkdir()

    monkeypatch.setattr(
        prepare_web_pages_spike, "WEB_SPIKE_ROOT", web_spike_root
    )

    with pytest.raises(ValueError, match="Staging path must be inside"):
        prepare_web_pages_spike.prepare_pages_site(outside)


def test_browser_url_uses_project_subpath_without_localhost_cdn_override() -> None:
    """Avoid Pygbag's localhost:8 development CDN rewrite during Pages tests."""
    staging = Path(".tatuy/web-spike/001_render_queue-551fc8d2")

    url = prepare_web_pages_spike.browser_url(
        staging, subpath="tatuy", port=8767
    )

    assert url == (
        "http://127.0.0.1:8767/tatuy/index.html?"
        "TATUY_BUILD=551fc8d2#"
    )

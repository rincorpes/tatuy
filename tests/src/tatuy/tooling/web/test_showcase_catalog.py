"""Showcase catalog discovery validates declared public target metadata."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tatuy.tooling.web.catalog import ShowcaseCatalogBuilder


def _write_target(
    repository: Path,
    relative: str,
    *,
    target_id: str = "fundamentals/rendering/demo",
    slug: str = "demo",
    title: str = "Demo",
    docs: str | None = "docs/learn/rendering.md",
    web: bool = True,
) -> Path:
    target = repository / relative
    target.mkdir(parents=True)
    (target / "app.py").write_text("def create_app(config=None): ...\n", encoding="utf-8")
    source = target.relative_to(repository).as_posix()
    docs_line = f"  docs: {docs}\n" if docs is not None else ""
    (target / "tatuy.web.yml").write_text(
        "showcase:\n"
        f"  id: {target_id}\n"
        f"  slug: {slug}\n"
        f"  title: {title}\n"
        "  description: Browser demo.\n"
        "  category: fundamental\n"
        "  tags:\n"
        "    - rendering\n"
        f"  source: {source}\n"
        f"{docs_line}"
        f"  web: {'true' if web else 'false'}\n",
        encoding="utf-8",
    )
    if docs is not None:
        docs_path = repository / docs
        docs_path.parent.mkdir(parents=True, exist_ok=True)
        docs_path.write_text("# Rendering\n", encoding="utf-8")
    if web:
        bundle = repository / "build" / "web" / "play" / slug
        bundle.mkdir(parents=True, exist_ok=True)
        (bundle / "index.html").write_text("runtime", encoding="utf-8")
    return target


def test_discover_returns_validated_catalog_entry(tmp_path: Path) -> None:
    _write_target(tmp_path, "examples/fundamentals/demo")

    entries = ShowcaseCatalogBuilder(tmp_path).discover()

    assert len(entries) == 1
    entry = entries[0]
    assert entry.id == "fundamentals/rendering/demo"
    assert entry.slug == "demo"
    assert entry.category == "fundamental"
    assert entry.tags == ("rendering",)
    assert entry.source == "examples/fundamentals/demo"
    assert entry.docs == "docs/learn/rendering.md"
    assert entry.playable is True
    assert entry.url == "showcase/demo/"
    assert entry.entrypoint == "play/demo/index.html"


def test_build_replaces_manifest_with_deterministic_catalog(tmp_path: Path) -> None:
    _write_target(tmp_path, "examples/fundamentals/demo")
    manifest = tmp_path / "build" / "web" / "manifest.json"
    manifest.write_text('{"targets": [{"slug": "stale"}]}\n', encoding="utf-8")

    result = ShowcaseCatalogBuilder(tmp_path).build()
    payload = json.loads(result.read_text(encoding="utf-8"))

    assert result == manifest
    assert [entry["id"] for entry in payload["targets"]] == [
        "fundamentals/rendering/demo"
    ]
    assert payload["targets"][0]["playable"] is True
    assert (tmp_path / "build" / "web" / ".nojekyll").exists()


def test_duplicate_catalog_ids_fail(tmp_path: Path) -> None:
    _write_target(tmp_path, "examples/fundamentals/one", slug="one")
    _write_target(tmp_path, "examples/fundamentals/two", slug="two")

    with pytest.raises(ValueError, match="Duplicate showcase id"):
        ShowcaseCatalogBuilder(tmp_path).discover()


def test_missing_required_title_fails(tmp_path: Path) -> None:
    target = _write_target(tmp_path, "examples/fundamentals/demo")
    profile = target / "tatuy.web.yml"
    profile.write_text(
        profile.read_text(encoding="utf-8").replace("  title: Demo\n", ""),
        encoding="utf-8",
    )

    with pytest.raises(TypeError, match="showcase.title"):
        ShowcaseCatalogBuilder(tmp_path).discover()


def test_declared_source_must_match_profile_directory(tmp_path: Path) -> None:
    target = _write_target(tmp_path, "examples/fundamentals/demo")
    profile = target / "tatuy.web.yml"
    profile.write_text(
        profile.read_text(encoding="utf-8").replace(
            "examples/fundamentals/demo", "examples/fundamentals/other"
        ),
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError, match="Showcase source"):
        ShowcaseCatalogBuilder(tmp_path).discover()


def test_web_target_requires_built_bundle(tmp_path: Path) -> None:
    _write_target(tmp_path, "examples/fundamentals/demo")
    bundle = tmp_path / "build" / "web" / "play" / "demo" / "index.html"
    bundle.unlink()

    with pytest.raises(FileNotFoundError, match="Web showcase bundle"):
        ShowcaseCatalogBuilder(tmp_path).discover()


def test_related_docs_must_exist(tmp_path: Path) -> None:
    _write_target(tmp_path, "examples/fundamentals/demo")
    (tmp_path / "docs" / "learn" / "rendering.md").unlink()

    with pytest.raises(FileNotFoundError, match="related docs"):
        ShowcaseCatalogBuilder(tmp_path).discover()


def test_non_web_catalog_entry_does_not_require_bundle(tmp_path: Path) -> None:
    _write_target(
        tmp_path,
        "examples/fundamentals/demo",
        docs=None,
        web=False,
    )

    [entry] = ShowcaseCatalogBuilder(tmp_path).discover()

    assert entry.web is False
    assert entry.playable is False

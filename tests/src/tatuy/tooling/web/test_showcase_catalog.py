"""Showcase catalog discovery validates declared public target metadata."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tatuy.tooling.web.catalog import ShowcaseCatalogBuilder


PROJECT_ROOT = Path(__file__).resolve().parents[5]


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
        (bundle / "build.json").write_text(
            json.dumps(
                {
                    "build_id": "12345678",
                    "source": source,
                    "commit_sha": "abc123",
                    "tatuy_version": "0.1.0",
                    "bridge": "pygbag",
                    "bridge_version": "0.9.3",
                    "python_version": "3.12.15",
                }
            ),
            encoding="utf-8",
        )
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


def test_discover_includes_existing_browser_thumbnail(tmp_path: Path) -> None:
    _write_target(tmp_path, "examples/fundamentals/demo")
    thumbnail = tmp_path / "build" / "web" / "assets" / "thumbnails" / "demo.png"
    thumbnail.parent.mkdir(parents=True)
    thumbnail.write_bytes(b"png")

    [entry] = ShowcaseCatalogBuilder(tmp_path).discover()

    assert entry.screenshot == "assets/thumbnails/demo.png"


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


def test_metadata_only_discovery_does_not_require_built_bundle(tmp_path: Path) -> None:
    _write_target(tmp_path, "examples/fundamentals/demo")
    bundle = tmp_path / "build" / "web" / "play" / "demo" / "index.html"
    bundle.unlink()

    [entry] = ShowcaseCatalogBuilder(tmp_path).discover(
        require_playable_bundles=False
    )

    assert entry.web is True
    assert entry.playable is False
    assert entry.source == "examples/fundamentals/demo"


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


def test_repository_public_v0_profiles_are_classified_and_valid(tmp_path: Path) -> None:
    playable_slugs = {
        "render-queue",
        "scene-on-present",
        "multiple-scenes",
        "controlled-movement",
        "ui-button",
        "snake",
        "procedural-tree",
        "infection-arena",
    }
    for slug in playable_slugs:
        bundle = tmp_path / "play" / slug
        bundle.mkdir(parents=True)
        (bundle / "index.html").write_text("runtime", encoding="utf-8")
        (bundle / "build.json").write_text(
            json.dumps(
                {
                    "build_id": f"{slug}-build",
                    "source": "examples/demo",
                    "commit_sha": "abc123",
                    "tatuy_version": "0.1.0",
                    "bridge": "pygbag",
                    "bridge_version": "0.9.3",
                    "python_version": "3.12.15",
                }
            ),
            encoding="utf-8",
        )

    entries = ShowcaseCatalogBuilder(
        PROJECT_ROOT,
        targets_root=PROJECT_ROOT / "examples",
        output_root=tmp_path,
    ).discover()
    by_id = {entry.id: entry for entry in entries}

    assert set(by_id) == {
        "fundamentals/audio",
        "fundamentals/rendering/render-queue",
        "fundamentals/scenes/on-present",
        "fundamentals/scenes/multiple-scenes",
        "fundamentals/movement/controlled-movement",
        "fundamentals/ui/button",
        "games/pong",
        "games/breakout",
        "games/snake",
        "games/asteroids",
        "experiments/breakout-prototype",
        "experiments/entities-pressure",
        "experiments/procedural-fire",
        "experiments/test-sandbox",
        "experiments/procedural-tree",
        "experiments/tree-explorer",
        "experiments/infection-arena",
    }
    assert {entry.slug for entry in by_id.values() if entry.web} == playable_slugs
    assert all(entry.playable is entry.web for entry in by_id.values())
    assert sum(entry.category == "game" for entry in by_id.values()) == 4
    assert sum(entry.category == "experiment" for entry in by_id.values()) == 7

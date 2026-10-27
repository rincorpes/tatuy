"""Static documentation-site configuration stays publishable and scoped."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import yaml

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 only
    import tomli as tomllib  # type: ignore[no-redef]


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPOSITORY_ROOT / "docs"
MKDOCS_CONFIG = REPOSITORY_ROOT / "mkdocs.yml"
PYPROJECT = REPOSITORY_ROOT / "pyproject.toml"


def _config() -> dict[str, Any]:
    loaded = yaml.safe_load(MKDOCS_CONFIG.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _nav_paths(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
        return
    if isinstance(value, list):
        for item in value:
            yield from _nav_paths(item)
        return
    if isinstance(value, dict):
        for item in value.values():
            yield from _nav_paths(item)


def test_docs_site_uses_project_subpath_and_normalized_output() -> None:
    config = _config()

    assert config["site_url"] == "https://rincorpes.github.io/tatuy/docs/"
    assert config["site_dir"] == "build/web/docs"
    assert config["use_directory_urls"] is True


def test_public_navigation_is_explicit_and_targets_existing_files() -> None:
    config = _config()
    nav = config["nav"]
    assert isinstance(nav, list)

    section_names = {
        next(iter(item))
        for item in nav
        if isinstance(item, dict) and item
    }
    assert {
        "Overview",
        "Getting Started",
        "Learn",
        "Guides",
        "Architecture",
        "Internals",
        "Examples",
    } <= section_names

    paths = list(_nav_paths(nav))
    assert paths
    for relative in paths:
        assert (DOCS_ROOT / relative).is_file(), relative


def test_private_ai_and_mcp_docs_are_excluded_from_public_build() -> None:
    config = _config()
    excluded = config["exclude_docs"]
    assert isinstance(excluded, str)
    assert "ai/" in excluded
    assert "internals/mcp/" in excluded

    nav_paths = list(_nav_paths(config["nav"]))
    assert all(not path.startswith("ai/") for path in nav_paths)
    assert all(not path.startswith("internals/mcp/") for path in nav_paths)


def test_public_docs_do_not_use_root_absolute_markdown_links() -> None:
    for path in DOCS_ROOT.rglob("*.md"):
        relative = path.relative_to(DOCS_ROOT).as_posix()
        if relative.startswith("ai/") or relative.startswith("internals/mcp/"):
            continue
        content = path.read_text(encoding="utf-8")
        assert "](/" not in content, relative


def test_docs_extra_owns_mkdocs_and_dev_includes_it() -> None:
    with PYPROJECT.open("rb") as stream:
        project = tomllib.load(stream)["project"]

    extras = project["optional-dependencies"]
    assert any(item.startswith("mkdocs ") for item in extras["docs"])
    assert any(item.startswith("mkdocs ") for item in extras["dev"])

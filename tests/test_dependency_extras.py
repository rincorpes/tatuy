"""Dependency extras keep runtime and browser build concerns separated."""

from __future__ import annotations

from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _optional_dependencies() -> dict[str, list[str]]:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)["project"]
    return project["optional-dependencies"]


def _names(dependencies: list[str]) -> set[str]:
    return {dependency.split()[0].lower() for dependency in dependencies}


def test_pygame_extra_uses_pygame_ce() -> None:
    extras = _optional_dependencies()

    assert _names(extras["pygame"]) == {"pygame-ce"}


def test_web_extra_contains_only_browser_build_requirements() -> None:
    extras = _optional_dependencies()

    assert _names(extras["web"]) == {"pygame-ce", "pygbag", "pyyaml"}


def test_dev_extra_includes_the_web_toolchain() -> None:
    extras = _optional_dependencies()
    dev = _names(extras["dev"])

    assert {"pygame-ce", "pygbag", "pyyaml"} <= dev
    assert "pygame" not in dev

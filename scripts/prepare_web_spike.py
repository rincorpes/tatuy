"""Stage a browser spike with the current local Tatuy source tree."""

from __future__ import annotations

import hashlib
import importlib.util
import shutil
from pathlib import Path
from typing import Any

from tatuy.configuration import ConfigurationLoader

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_TARGET = (
    REPOSITORY_ROOT
    / "examples"
    / "fundamentals"
    / "009_rendering"
    / "002_render_queue"
)
TATUY_SOURCE = REPOSITORY_ROOT / "src" / "tatuy"
STAGING_BASE = REPOSITORY_ROOT / ".tatuy" / "web-spike"
PURE_PYTHON_PACKAGES = ("onomasticon",)


def _package_source(package_name: str) -> Path:
    """Resolve one importable package directory from the active environment."""
    spec = importlib.util.find_spec(package_name)
    if spec is None or spec.submodule_search_locations is None:
        raise RuntimeError(f"Cannot resolve package {package_name!r}")
    return Path(next(iter(spec.submodule_search_locations)))


def _packaged_files(root: Path) -> list[Path]:
    """Return deterministic files copied into the browser archive."""
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or ".mypy_cache" in path.parts:
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        files.append(path)
    return sorted(files)


def _content_fingerprint() -> str:
    """Hash every source file that affects the staged application archive."""
    digest = hashlib.sha256()
    sources = [("main", SOURCE_TARGET), ("tatuy", TATUY_SOURCE)]
    sources.extend(
        (package_name, _package_source(package_name))
        for package_name in PURE_PYTHON_PACKAGES
    )

    for label, root in sources:
        for path in _packaged_files(root):
            relative = path.relative_to(root).as_posix()
            digest.update(f"{label}/{relative}\0".encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()[:8]


def _copy_package(package_name: str, staging_root: Path) -> None:
    """Bundle one importable pure-Python package into the staging archive."""
    shutil.copytree(
        _package_source(package_name),
        staging_root / package_name,
        ignore=shutil.ignore_patterns(
            "__pycache__",
            ".mypy_cache",
            "*.pyc",
            "*.pyo",
        ),
    )


def _browser_launcher(config: dict[str, Any]) -> str:
    """Return a generated cooperative launcher for the canonical target."""
    return f'''"""Generated Pygbag launcher for a canonical Tatuy target."""

from __future__ import annotations

import asyncio

# Pygbag discovers WASM packages from top-level imports in main.py.
import pygame

from app import create_app
from tatuy.engine.runtime.host import AsyncRuntimeHost

PYGAME_PRELOAD = pygame
WEB_CONFIG = {config!r}


async def main() -> None:
    app = create_app(WEB_CONFIG)
    await AsyncRuntimeHost().run(app.build())


asyncio.run(main())
'''


def prepare() -> Path:
    """Create a cache-safe Pygbag project containing Tatuy and dependencies."""
    STAGING_BASE.mkdir(parents=True, exist_ok=True)
    legacy_root = STAGING_BASE / SOURCE_TARGET.name
    if legacy_root.exists():
        shutil.rmtree(legacy_root)
    for stale_root in STAGING_BASE.glob(f"{SOURCE_TARGET.name}-*"):
        if stale_root.is_dir():
            shutil.rmtree(stale_root)

    staging_root = (
        STAGING_BASE / f"{SOURCE_TARGET.name}-{_content_fingerprint()}"
    )
    staging_root.mkdir()

    config = ConfigurationLoader.load_profile(
        SOURCE_TARGET / "tatuy.yml", "web"
    )
    (staging_root / "main.py").write_text(
        _browser_launcher(config),
        encoding="utf-8",
    )
    shutil.copy2(SOURCE_TARGET / "app.py", staging_root / "app.py")
    shutil.copytree(
        TATUY_SOURCE,
        staging_root / "tatuy",
        ignore=shutil.ignore_patterns(
            "__pycache__",
            ".mypy_cache",
            "*.pyc",
            "*.pyo",
        ),
    )
    for package_name in PURE_PYTHON_PACKAGES:
        _copy_package(package_name, staging_root)
    return staging_root


def browser_urls(staging: Path, *, port: int = 8766) -> tuple[str, str]:
    """Return cache-safe normal and interactive URLs for one staged build."""
    build_id = staging.name.rsplit("-", 1)[-1]
    base = (
        f"http://localhost:{port}/index.html?"
        f"PYGPI=http://localhost:{port}/cdn/&TATUY_BUILD={build_id}"
    )
    return f"{base}#", f"{base}&-i#"


def main() -> None:
    """Prepare the project and print the next Pygbag command and browser URLs."""
    staging = prepare()
    relative = staging.relative_to(REPOSITORY_ROOT)
    normal_url, interactive_url = browser_urls(staging)
    print(f"Prepared web spike at: {relative}")
    print(
        "Run: .\\.venv-web\\Scripts\\python.exe -m pygbag "
        "--PYBUILD 3.12 --ume_block 0 --port 8766 "
        f"{relative}"
    )
    print(f"Open: {normal_url}")
    print(f"Debug: {interactive_url}")


if __name__ == "__main__":
    main()

"""Compatibility helper for staging the canonical Tatuy browser target."""

from __future__ import annotations

from pathlib import Path

from tatuy.tooling.web import WebTargetBuilder

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


def _builder() -> WebTargetBuilder:
    """Create the reusable W6 builder with legacy spike staging paths."""
    return WebTargetBuilder(
        REPOSITORY_ROOT,
        staging_root=STAGING_BASE,
        tatuy_source=TATUY_SOURCE,
        pure_python_packages=PURE_PYTHON_PACKAGES,
    )


def prepare() -> Path:
    """Stage the canonical target through the reusable web-target builder."""
    staging, _ = _builder().prepare(SOURCE_TARGET)
    return staging


def browser_urls(staging: Path, *, port: int = 8766) -> tuple[str, str]:
    """Return cache-safe normal and interactive URLs for one staged build."""
    build_id = staging.name.rsplit("-", 1)[-1]
    base = (
        f"http://localhost:{port}/index.html?"
        f"PYGPI=http://localhost:{port}/cdn/&TATUY_BUILD={build_id}"
    )
    return f"{base}#", f"{base}&-i#"


def main() -> None:
    """Prepare the canonical target and print local Pygbag development steps."""
    staging = prepare()
    relative = staging.relative_to(REPOSITORY_ROOT)
    normal_url, interactive_url = browser_urls(staging)
    print(f"Prepared web target at: {relative}")
    print(
        "Run: .\\.venv-web\\Scripts\\python.exe -m pygbag "
        "--PYBUILD 3.12 --ume_block 0 --port 8766 "
        f"{relative}"
    )
    print(f"Open: {normal_url}")
    print(f"Debug: {interactive_url}")


if __name__ == "__main__":
    main()

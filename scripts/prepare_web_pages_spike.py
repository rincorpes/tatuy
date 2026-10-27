"""Stage a Pygbag build under a GitHub Pages-style project subpath."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WEB_SPIKE_ROOT = REPOSITORY_ROOT / ".tatuy" / "web-spike"
PAGES_ROOT = REPOSITORY_ROOT / ".tatuy" / "web-pages"
DEFAULT_SUBPATH = "tatuy"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8767


def _validate_staging(staging: Path) -> Path:
    """Return an absolute staging path constrained to the ignored web-spike tree."""
    resolved = staging.resolve()
    try:
        resolved.relative_to(WEB_SPIKE_ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"Staging path must be inside {WEB_SPIKE_ROOT}") from exc
    return resolved


def prepare_pages_site(
    staging: Path, *, subpath: str = DEFAULT_SUBPATH
) -> Path:
    """Copy one static Pygbag build beneath a project-pages style subpath."""
    staging = _validate_staging(staging)
    build_root = staging / "build" / "web"
    if not build_root.is_dir():
        raise FileNotFoundError(
            f"Pygbag static build not found at {build_root}. "
            "Run pygbag with --build for this staging directory first."
        )

    site_root = PAGES_ROOT
    target_root = site_root / subpath
    if site_root.exists():
        shutil.rmtree(site_root)
    target_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(build_root, target_root)
    (site_root / ".nojekyll").touch()
    return site_root


def browser_url(
    staging: Path,
    *,
    subpath: str = DEFAULT_SUBPATH,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
) -> str:
    """Return a URL that exercises the static build below a project subpath."""
    build_id = staging.name.rsplit("-", 1)[-1]
    return f"http://{host}:{port}/{subpath}/index.html?TATUY_BUILD={build_id}#"


def main() -> None:
    """Stage an existing Pygbag build and print the local Pages-style test steps."""
    parser = argparse.ArgumentParser()
    parser.add_argument("staging", type=Path)
    parser.add_argument("--subpath", default=DEFAULT_SUBPATH)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    staging = _validate_staging(args.staging)
    site_root = prepare_pages_site(staging, subpath=args.subpath)
    relative_site = site_root.relative_to(REPOSITORY_ROOT)
    print(f"Prepared Pages-style site at: {relative_site}")
    print(
        "Serve: poetry run python -m http.server "
        f"{args.port} --bind {args.host} --directory {relative_site}"
    )
    print(
        "Open: "
        + browser_url(
            staging,
            subpath=args.subpath,
            host=args.host,
            port=args.port,
        )
    )


if __name__ == "__main__":
    main()

"""Build and optionally serve the complete Tatuy web showcase locally."""

from __future__ import annotations

import argparse
import subprocess
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WEB_OUTPUT = REPOSITORY_ROOT / "build" / "web"


def build_showcase() -> None:
    """Run the same static showcase build stages used by GitHub Actions."""
    commands = (
        (
            sys.executable,
            "scripts/build_showcase_catalog.py",
            "--metadata-only",
        ),
        (sys.executable, "scripts/build_showcase_targets.py"),
        (sys.executable, "-m", "mkdocs", "build", "--strict"),
        (sys.executable, "scripts/build_showcase_site.py"),
        (sys.executable, "scripts/validate_web_output.py"),
    )
    for command in commands:
        subprocess.run(command, cwd=REPOSITORY_ROOT, check=True)


def serve_showcase(host: str, port: int) -> None:
    """Serve generated web output until interrupted."""
    handler = partial(SimpleHTTPRequestHandler, directory=str(WEB_OUTPUT))
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Tatuy showcase: http://{host}:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> None:
    """Build the showcase and optionally start a local preview server."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Serve build/web after the showcase build completes.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    build_showcase()
    if args.serve:
        serve_showcase(args.host, args.port)


if __name__ == "__main__":
    main()

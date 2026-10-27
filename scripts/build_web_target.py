"""Build one Tatuy target into normalized static browser output."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tatuy.tooling.web import PygbagPackager, WebTargetBuilder

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = Path("examples/fundamentals/009_rendering/002_render_queue")


def main() -> None:
    """Build one target and print normalized web output locations."""
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", type=Path, default=DEFAULT_TARGET)
    parser.add_argument(
        "--pygbag-python",
        default=sys.executable,
        help="Python executable whose environment provides pygbag.",
    )
    args = parser.parse_args()

    packager = PygbagPackager(command=(args.pygbag_python, "-m", "pygbag"))
    builder = WebTargetBuilder(REPOSITORY_ROOT, packager=packager)
    result = builder.build(args.target)
    print(f"Built target: {result.metadata.slug}")
    print(f"Output: {result.output.relative_to(REPOSITORY_ROOT)}")
    print(f"Manifest: {result.manifest.relative_to(REPOSITORY_ROOT)}")
    print(f"Build ID: {result.build_id}")


if __name__ == "__main__":
    main()

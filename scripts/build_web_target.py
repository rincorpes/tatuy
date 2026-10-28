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
    parser.add_argument(
        "--allow-unsupported-sound-format",
        action="store_true",
        help=(
            "Temporarily suppress Pygbag's sound-format validation for local "
            "browser testing. Public showcase assets should use OGG instead."
        ),
    )
    args = parser.parse_args()

    packager = PygbagPackager(
        command=(args.pygbag_python, "-m", "pygbag"),
        disable_sound_format_error=args.allow_unsupported_sound_format,
    )
    builder = WebTargetBuilder(REPOSITORY_ROOT, packager=packager)
    result = builder.build(args.target)
    print(f"Built target: {result.metadata.slug}")
    print(f"Output: {result.output.relative_to(REPOSITORY_ROOT)}")
    print(f"Manifest: {result.manifest.relative_to(REPOSITORY_ROOT)}")
    print(f"Build ID: {result.build_id}")


if __name__ == "__main__":
    main()

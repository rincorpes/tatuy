"""Generate the validated Tatuy showcase catalog manifest."""

from __future__ import annotations

import argparse
from pathlib import Path

from tatuy.tooling.web.catalog import ShowcaseCatalogBuilder

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Validate showcase metadata or build the generated catalog manifest."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Validate showcase declarations without requiring browser bundles.",
    )
    args = parser.parse_args()

    builder = ShowcaseCatalogBuilder(REPOSITORY_ROOT)
    if args.metadata_only:
        entries = builder.discover(require_playable_bundles=False)
        web_targets = sum(1 for entry in entries if entry.web)
        print(
            f"Validated {len(entries)} showcase target(s); "
            f"{web_targets} browser target(s) declared."
        )
        return

    manifest = builder.build()
    print(f"Showcase catalog: {manifest.relative_to(REPOSITORY_ROOT)}")


if __name__ == "__main__":
    main()

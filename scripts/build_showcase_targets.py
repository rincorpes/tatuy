"""Build every showcase target that declares browser support."""

from __future__ import annotations

import sys
from pathlib import Path

from tatuy.tooling.web import PygbagPackager, ShowcaseCatalogBuilder, WebTargetBuilder

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Build all ``showcase.web: true`` targets from validated metadata."""
    catalog = ShowcaseCatalogBuilder(REPOSITORY_ROOT)
    entries = catalog.discover(require_playable_bundles=False)
    targets = [entry for entry in entries if entry.web]
    packager = PygbagPackager(command=(sys.executable, "-m", "pygbag"))
    builder = WebTargetBuilder(REPOSITORY_ROOT, packager=packager)

    for entry in targets:
        result = builder.build(Path(entry.source))
        print(
            f"Built {entry.id}: "
            f"{result.output.relative_to(REPOSITORY_ROOT)}"
        )

    print(f"Built {len(targets)} showcase browser target(s).")


if __name__ == "__main__":
    main()

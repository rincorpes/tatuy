"""Generate the validated Tatuy showcase catalog manifest."""

from __future__ import annotations

from pathlib import Path

from tatuy.tooling.web.catalog import ShowcaseCatalogBuilder

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Build the showcase catalog and print the generated manifest path."""
    builder = ShowcaseCatalogBuilder(REPOSITORY_ROOT)
    manifest = builder.build()
    print(f"Showcase catalog: {manifest.relative_to(REPOSITORY_ROOT)}")


if __name__ == "__main__":
    main()

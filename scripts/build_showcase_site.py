"""Compose the Tatuy showcase shell around existing web outputs."""

from __future__ import annotations

from pathlib import Path

from tatuy.tooling.web.site import ShowcaseSiteBuilder

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Build the static showcase shell into ``build/web``."""
    output = ShowcaseSiteBuilder(REPOSITORY_ROOT).build()
    print(f"Showcase site: {output.relative_to(REPOSITORY_ROOT)}")


if __name__ == "__main__":
    main()

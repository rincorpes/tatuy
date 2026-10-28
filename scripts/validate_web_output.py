"""Validate generated Tatuy web output before publication."""

from __future__ import annotations

from pathlib import Path

from tatuy.tooling.web import WebOutputBasePathValidator

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WEB_OUTPUT = REPOSITORY_ROOT / "build" / "web"


def main() -> None:
    """Run static publication checks against the composed web output."""
    WebOutputBasePathValidator().validate(WEB_OUTPUT)
    manifest = WEB_OUTPUT / "manifest.json"
    if not manifest.is_file():
        raise FileNotFoundError(f"Showcase manifest not found: {manifest}")
    if not (WEB_OUTPUT / ".nojekyll").is_file():
        raise FileNotFoundError("GitHub Pages .nojekyll marker is missing")
    print("Web output validation passed.")


if __name__ == "__main__":
    main()

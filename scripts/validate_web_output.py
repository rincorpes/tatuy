"""Validate generated Tatuy web output before publication."""

from __future__ import annotations

from pathlib import Path

from tatuy.tooling.web import (
    WebOutputBasePathValidator,
    WebOutputStructureValidator,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WEB_OUTPUT = REPOSITORY_ROOT / "build" / "web"


def main() -> None:
    """Run static publication checks against the composed web output."""
    WebOutputStructureValidator().validate(WEB_OUTPUT)
    WebOutputBasePathValidator().validate(WEB_OUTPUT)
    print("Web output validation passed.")


if __name__ == "__main__":
    main()

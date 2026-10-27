"""Web compatibility documentation tracks every runnable fundamental."""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FUNDAMENTALS_ROOT = PROJECT_ROOT / "examples" / "fundamentals"
MATRIX_PATH = PROJECT_ROOT / "docs" / "examples" / "web-compatibility.md"


def _runnable_targets() -> set[str]:
    targets: set[str] = set()
    for app_file in FUNDAMENTALS_ROOT.rglob("app.py"):
        target = app_file.parent.relative_to(FUNDAMENTALS_ROOT).as_posix()
        targets.add(target)
    return targets


def _matrix_targets() -> set[str]:
    content = MATRIX_PATH.read_text(encoding="utf-8")
    targets: set[str] = set()
    for line in content.splitlines():
        if not line.startswith("| `") or line.count("|") < 9:
            continue
        match = re.match(r"\| `([^`]+)` \|", line)
        if match:
            targets.add(match.group(1))
    return targets


def test_web_compatibility_matrix_tracks_every_runnable_fundamental() -> None:
    assert _matrix_targets() == _runnable_targets()


def test_web_compatibility_matrix_keeps_current_scope_fundamentals_only() -> None:
    content = MATRIX_PATH.read_text(encoding="utf-8")

    assert "current showcase scope is **fundamentals only**" in content
    assert "does not include experiments or games" in content

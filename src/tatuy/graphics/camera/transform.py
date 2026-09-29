from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ViewTransform:
    """Translation in logical view units; positive offsets move content."""

    offset_x: float = 0.0
    offset_y: float = 0.0

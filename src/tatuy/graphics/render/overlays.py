from __future__ import annotations

from dataclasses import dataclass

from tatuy.graphics.color import ColorRGBA


@dataclass(frozen=True)
class ScreenOverlay:
    """A uniform overlay covering the logical viewport."""

    color: ColorRGBA

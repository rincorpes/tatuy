from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from tatuy.geometry.size import Size


class ViewportMode(str, Enum):
    """
    Viewport scaling modes.
    """

    FIT = "fit"  # letterbox
    FILL = "fill"  # crop


@dataclass
class ViewportState:
    """
    Current state of the viewport.
    """

    virtual_w: int
    virtual_h: int

    window_w: int
    window_h: int

    mode: ViewportMode
    scale: float

    # viewport rect in screen pixels where the virtual canvas lands
    # (can be larger than window in FILL mode -> offsets can be negative)
    viewport_w: int
    viewport_h: int
    offset_x: int
    offset_y: int

    def update(self, size: Size):
        self.virtual_w = size.width
        self.virtual_h = size.height
        self.window_w = size.width
        self.window_h = size.height

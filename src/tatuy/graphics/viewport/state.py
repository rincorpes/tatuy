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

    def resize_window(self, size: Size) -> None:
        """Resize the host window while preserving the logical game resolution."""
        self.window_w = max(1, size.width)
        self.window_h = max(1, size.height)
        scale_x = self.window_w / self.virtual_w
        scale_y = self.window_h / self.virtual_h
        self.scale = (
            min(scale_x, scale_y)
            if self.mode == ViewportMode.FIT
            else max(scale_x, scale_y)
        )
        self.viewport_w = max(1, round(self.virtual_w * self.scale))
        self.viewport_h = max(1, round(self.virtual_h * self.scale))
        self.offset_x = round((self.window_w - self.viewport_w) / 2)
        self.offset_y = round((self.window_h - self.viewport_h) / 2)

    def contains_window_point(self, x: int, y: int) -> bool:
        """Return whether a host-window point lands inside the logical viewport."""
        return (
            self.offset_x <= x < self.offset_x + self.viewport_w
            and self.offset_y <= y < self.offset_y + self.viewport_h
        )

    def window_to_virtual(self, x: int, y: int) -> tuple[int, int]:
        """Map host-window pixels into logical game coordinates."""
        return (
            int((x - self.offset_x) / self.scale),
            int((y - self.offset_y) / self.scale),
        )

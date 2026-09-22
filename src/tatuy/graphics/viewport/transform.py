from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ViewportTransform:
    """
    Viewport transformation for coordinate mapping.
    """

    ox: int = 0
    oy: int = 0
    s: float = 1.0

    def map_xy(self, x: int, y: int) -> tuple[int, int]:
        """
        Map the given (x, y) coordinates using the viewport transformation.
        """
        return (
            int(round(self.ox + x * self.s)),
            int(round(self.oy + y * self.s)),
        )

    def map_wh(self, w: int, h: int) -> tuple[int, int]:
        """
        Map the given width and height using the viewport transformation.
        """
        return (int(round(w * self.s)), int(round(h * self.s)))

    def set(self, offset_x: int, offset_y: int, scale: float):
        """
        Set the viewport transform.
        """
        self.ox = int(offset_x)
        self.oy = int(offset_y)
        self.s = float(scale)

    def clear(self):
        """Clear the viewport transform (reset to defaults)."""
        self.ox = 0
        self.oy = 0
        self.s = 1.0

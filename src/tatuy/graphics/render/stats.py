from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RenderStats:
    """
    Statistics about the rendering process for a single frame.
    """

    packets: int = 0
    ops: int = 0
    draw_groups: int = 0  # approx ok
    renderables: int = 0

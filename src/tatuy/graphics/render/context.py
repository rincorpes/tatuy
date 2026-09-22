from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tatuy.graphics.render.stats import RenderStats
from tatuy.graphics.viewport.state import ViewportState


@dataclass
class RenderContext:
    """
    Context for rendering a single frame.
    """

    viewport: ViewportState
    debug_overlay: bool = False
    frame_ms: float = 0.0
    stats: RenderStats = field(default_factory=RenderStats)
    meta: dict[str, Any] = field(default_factory=dict)

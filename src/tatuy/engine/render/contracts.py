"""Rendering coordination contracts owned by the engine boundary."""

from __future__ import annotations

from typing import Protocol, Sequence

from tatuy.backend import Backend
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.packets import FramePacket


class FrameRenderDriver(Protocol):
    """Render prepared frame data and present it independently."""

    def render_frame_content(
        self,
        backend: Backend,
        ctx: RenderContext,
        packets: Sequence[FramePacket],
    ) -> None:
        """Render frame contents without presenting the back buffer."""

    def present_frame(self, backend: Backend, ctx: RenderContext) -> None:
        """Present previously rendered frame contents."""

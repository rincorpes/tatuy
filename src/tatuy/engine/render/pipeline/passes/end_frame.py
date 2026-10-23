"""End-frame render pass implementation."""

from dataclasses import dataclass
from typing import Sequence

from tatuy.backend import Backend
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.executor import RenderExecutor
from tatuy.graphics.render.packets import FramePacket


@dataclass
class EndFramePass:
    """Present the current backend frame."""

    name: str = "EndFrame"

    def run(
        self,
        backend: Backend,
        ctx: RenderContext,
        packets: Sequence[FramePacket],
        executor: RenderExecutor,
    ) -> None:
        """Signal the end of the frame to the backend."""
        del ctx, packets, executor
        backend.renderer.end_frame()

"""Begin-frame render pass."""

from dataclasses import dataclass
from typing import Sequence

from tatuy.backend import Backend
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.executor import RenderExecutor
from tatuy.graphics.render.packets import FramePacket


@dataclass
class BeginFramePass:
    """Signal the start of a new frame to the backend."""

    name: str = "BeginFrame"

    def run(
        self,
        backend: Backend,
        ctx: RenderContext,
        packets: Sequence[FramePacket],
        executor: RenderExecutor,
    ) -> None:
        """Begin a backend frame."""
        del ctx, packets, executor
        if (
            not hasattr(backend.renderer, "begin_frame")
            or backend.renderer is None
        ):
            raise NotImplementedError(
                "Backend does not support begin_frame method"
            )
        backend.renderer.begin_frame()

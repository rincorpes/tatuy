"""
Begin Frame Render Pass
"""

from dataclasses import dataclass

from tatuy.backend import Backend
from tatuy.graphics.render.context import RenderContext
from tatuy.engine.loop.frame_packet import FramePacket


@dataclass
class BeginFramePass:
    """
    Begin Frame Render Pass.
    This pass signals the start of a new frame to the backend.
    """

    name: str = "BeginFrame"

    # Justification: some arguments are unused but required by the protocol
    # pylint: disable=unused-argument
    def run(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ):
        """Run the begin frame pass."""
        if (
            not hasattr(backend.renderer, "begin_frame")
            or backend.renderer is None
        ):
            raise NotImplementedError(
                "Backend does not support begin_frame method"
            )
        backend.renderer.begin_frame()

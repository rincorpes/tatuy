"""
End Frame render pass implementation.
"""

from dataclasses import dataclass

from tatuy.backend import Backend
from tatuy.graphics.render.context import RenderContext
from tatuy.engine.loop.frame_packet import FramePacket


@dataclass
class EndFramePass:
    """
    End Frame Render Pass.
    This pass signals the end of the current frame to the backend.
    """

    name: str = "EndFrame"

    # Justification: some arguments are unused but required by the protocol
    # pylint: disable=unused-argument
    def run(
        self, backend: Backend, ctx: RenderContext, packets: list[FramePacket]
    ):
        """Run the end frame pass."""
        # Signal the end of the frame to the backend
        backend.renderer.end_frame()

from __future__ import annotations
from dataclasses import dataclass

from tatuy.graphics.render.packets import RenderPacket


@dataclass(frozen=True)
class FramePacket:
    """
    A packet representing a frame to be rendered, associated with a specific scene
    and indicating whether it is an overlay.
    """

    scene_id: str
    is_overlay: bool
    packet: RenderPacket

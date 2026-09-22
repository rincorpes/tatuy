"""
Render pass base protocol.
"""

from __future__ import annotations

from typing import Protocol

from tatuy.backend import Backend
from tatuy.engine.loop.frame_packet import FramePacket
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.packets import RenderPacket


class RenderPacketPass(Protocol):
    """
    Render pass protocol.

    :ivar name: str: Name of the render pass.
    """

    @property
    def name(self) -> str: ...

    def run(
        self,
        backend: Backend,
        ctx: RenderContext,
        packets: list[RenderPacket],
    ) -> None:
        """
        Run the render pass.

        :param backend: Backend: The rendering backend.
        :type backend: Backend

        :param ctx: RenderContext: The rendering context.
        :type ctx: RenderContext

        :param packets: list[RenderPacket]: List of render packets to process.
        :type packets: list[RenderPacket]
        """


class FramePacketPass(Protocol):
    """
    Frame pass protocol.

    :ivar name: str: Name of the render pass.
    """

    @property
    def name(self) -> str: ...

    def run(
        self,
        backend: Backend,
        ctx: RenderContext,
        packets: list[FramePacket],
    ) -> None:
        """
        Run the render pass.

        :param backend: Backend: The rendering backend.
        :type backend: Backend

        :param ctx: RenderContext: The rendering context.
        :type ctx: RenderContext

        :param packets: list[RenderPacket]: List of render packets to process.
        :type packets: list[RenderPacket]
        """

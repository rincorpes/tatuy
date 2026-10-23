"""Render-pass contracts for prepared frame data."""

from __future__ import annotations

from typing import Protocol, Sequence

from tatuy.backend import Backend
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.executor import RenderExecutor
from tatuy.graphics.render.packets import FramePacket


class FramePacketPass(Protocol):
    """Consume prepared frame packets as one render-pipeline stage."""

    @property
    def name(self) -> str:
        """Return the pass name used by diagnostics."""

    def run(
        self,
        backend: Backend,
        ctx: RenderContext,
        packets: Sequence[FramePacket],
        executor: RenderExecutor,
    ) -> None:
        """Run the render pass against prepared frame data."""

"""Draw screen-space layers and scene overlays."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from tatuy.backend import Backend
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.executor import RenderExecutor
from tatuy.graphics.render.packets import FramePacket


@dataclass
class UIPass:
    """Render selected screen-space layers and optional overlay scenes."""

    name: str = "UIPass"
    layers: tuple[str, ...] = ("ui",)
    include_overlays: bool = True

    def run(
        self,
        backend: Backend,
        ctx: RenderContext,
        packets: Sequence[FramePacket],
        executor: RenderExecutor,
    ) -> None:
        """Execute screen-space operations with viewport transforms cleared."""
        backend.renderer.viewport_transform.clear()
        backend.renderer.clip.clear()

        try:
            for frame in packets:
                if frame.is_overlay:
                    if not self.include_overlays:
                        continue
                    operations = frame.packet.operations
                else:
                    operations = tuple(
                        operation
                        for layer in self.layers
                        for operation in frame.packet.layer_operations(layer)
                    )

                if not operations:
                    continue

                ctx.stats.packets += 1
                ctx.stats.renderables += len(operations)
                ctx.stats.draw_groups += 1
                executor.execute(backend, operations)
        finally:
            backend.renderer.clip.clear()
            backend.renderer.viewport_transform.clear()

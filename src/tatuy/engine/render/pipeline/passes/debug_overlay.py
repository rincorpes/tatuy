from __future__ import annotations

from dataclasses import dataclass, field

from tatuy.backend import Backend
from tatuy.engine.loop.frame_packet import FramePacket
from tatuy.graphics.render.context import RenderContext


@dataclass
class FpsSampler:
    sample_period_s: float = 0.25

    _elapsed_s: float = field(default=0.0, init=False)
    _frames: int = field(default=0, init=False)
    value: float | None = field(default=None, init=False)

    def update(self, frame_ms: float) -> float | None:
        if frame_ms <= 0:
            return self.value

        self._elapsed_s += frame_ms / 1000
        self._frames += 1

        if self._elapsed_s >= self.sample_period_s:
            self.value = self._frames / self._elapsed_s
            self._elapsed_s = 0.0
            self._frames = 0

        return self.value


@dataclass
class DebugOverlayPass:
    name: str = "DebugOverlayPass"
    sampler: FpsSampler = field(default_factory=FpsSampler)

    def run(
        self,
        backend: Backend,
        ctx: RenderContext,
        packets: list[FramePacket],
    ) -> None:
        if not ctx.debug_overlay:
            return

        fps = self.sampler.update(ctx.frame_ms)

        label = "FPS: --" if fps is None else f"FPS: {fps:.1f}"

        # Debug information is rendered in screen coordinates.
        backend.renderer.viewport_transform.clear()
        backend.renderer.clip.clear()

        backend.renderer.text.draw(
            8,
            8,
            label,
            (255, 255, 0),
            18,
            None,
        )

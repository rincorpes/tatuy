"""Debug overlay render pass."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from tatuy.backend import Backend
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.executor import RenderExecutor
from tatuy.graphics.render.packets import FramePacket


@dataclass
class FpsSampler:
    """Sample frame durations into a low-frequency FPS value."""

    sample_period_s: float = 0.25
    _elapsed_s: float = field(default=0.0, init=False)
    _frames: int = field(default=0, init=False)
    value: float | None = field(default=None, init=False)

    def update(self, frame_ms: float) -> float | None:
        """Add one frame duration and return the latest sampled FPS."""
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
    """Draw engine diagnostics after scene content."""

    name: str = "DebugOverlayPass"
    sampler: FpsSampler = field(default_factory=FpsSampler)

    def run(
        self,
        backend: Backend,
        ctx: RenderContext,
        packets: Sequence[FramePacket],
        executor: RenderExecutor,
    ) -> None:
        """Draw the FPS label when debug overlays are enabled."""
        del packets, executor
        if not ctx.debug_overlay:
            return

        fps = self.sampler.update(ctx.frame_ms)
        label = "FPS: --" if fps is None else f"FPS: {fps:.1f}"

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

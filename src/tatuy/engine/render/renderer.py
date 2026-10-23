"""Frame rendering coordination."""

from __future__ import annotations

from tatuy.backend import Backend
from tatuy.capture.service import CaptureService
from tatuy.engine.render.contracts import FrameRenderDriver
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.packets import FramePacket
from tatuy.graphics.viewport.service import ViewportService
from tatuy.tooling.profiler import profiler
from tatuy.window.service import WindowService


class FrameRenderer:
    """Coordinate viewport sizing, frame rendering, capture, and presentation."""

    def __init__(
        self,
        backend: Backend,
        pipeline: FrameRenderDriver,
        viewport: ViewportService,
        window: WindowService,
        capture: CaptureService,
        *,
        debug_overlay: bool = False,
    ) -> None:
        self._backend = backend
        self._driver = pipeline
        self._viewport = viewport
        self._window = window
        self._capture = capture
        self._debug_overlay = debug_overlay

    def render(
        self,
        packets: list[FramePacket],
        dt: float,
    ) -> None:
        """Render and present one frame when the backend is initialized."""
        if not self._backend.initialized:
            return

        with profiler.span("viewport.resize", "render"):
            self._viewport.resize(self._window.size)

        context = RenderContext(
            viewport=self._viewport.state,
            debug_overlay=self._debug_overlay,
            frame_ms=dt * 1000,
        )

        with profiler.span("render_frame_content", "render"):
            self._driver.render_frame_content(
                self._backend,
                context,
                packets,
            )

        with profiler.span("capture.after_render", "render"):
            self._capture.after_render()

        with profiler.span("present_frame", "render"):
            self._driver.present_frame(
                self._backend,
                context,
            )

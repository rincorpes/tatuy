from __future__ import annotations

from tatuy.geometry.size import Size
from tatuy.graphics.viewport.state import ViewportMode, ViewportState


class ViewportService:
    def __init__(self) -> None:
        self._state: ViewportState | None = None

    @property
    def state(self) -> ViewportState:
        if self._state is None:
            raise RuntimeError("Viewport has not been initialized")

        return self._state

    def initialize(self, size: Size) -> None:
        self._state = ViewportState(
            virtual_w=size.width,
            virtual_h=size.height,
            window_w=size.width,
            window_h=size.height,
            mode=ViewportMode.FIT,
            scale=1.0,
            viewport_w=size.width,
            viewport_h=size.height,
            offset_x=0,
            offset_y=0,
        )

    def resize(self, size: Size) -> None:
        """Resize the host window while preserving the initialized logical size."""
        if self._state is None:
            self.initialize(size)
            return
        self._state.resize_window(size)

    def contains_window_point(self, x: int, y: int) -> bool:
        """Return whether a host-window point lies inside the logical viewport."""
        if self._state is None:
            return False
        return self._state.contains_window_point(x, y)

    def window_to_virtual(self, x: int, y: int) -> tuple[int, int]:
        """Map host-window pixels into logical game coordinates."""
        if self._state is None:
            return (x, y)
        return self._state.window_to_virtual(x, y)

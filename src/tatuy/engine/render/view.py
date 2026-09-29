from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from tatuy.backend import Backend
from tatuy.geometry.size import Size
from tatuy.graphics.camera.transform import ViewTransform
from tatuy.graphics.viewport.state import ViewportState
from tatuy.math.vec2 import Vec2


@contextmanager
def world_drawing_scope(
    backend: Backend,
    viewport: ViewportState,
    view: ViewTransform,
) -> Iterator[None]:
    """Establish world mapping and a stationary viewport clip."""
    renderer = backend.renderer
    transform = renderer.viewport_transform

    try:
        # Establish the clip using viewport placement only.
        transform.set(
            viewport.offset_x,
            viewport.offset_y,
            viewport.scale,
        )
        renderer.clip.set(
            Vec2(0, 0),
            Size(
                viewport.virtual_w,
                viewport.virtual_h,
            ),
        )

        # Apply view translation inside the stationary viewport.
        transform.set(
            round(viewport.offset_x + viewport.scale * view.offset_x),
            round(viewport.offset_y + viewport.scale * view.offset_y),
            viewport.scale,
        )

        yield
    finally:
        try:
            renderer.clip.clear()
        finally:
            transform.clear()

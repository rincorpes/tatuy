"""Prepared rendering data passed from scene presentation to render execution."""

from __future__ import annotations

from dataclasses import dataclass, field

from tatuy.graphics.camera.transform import ViewTransform
from tatuy.graphics.render.overlays import ScreenOverlay
from tatuy.graphics.render.queue import DrawOperation, Layer


@dataclass(frozen=True)
class RenderPacket:
    """Immutable batch of prepared draw operations for one scene."""

    operations: tuple[DrawOperation, ...] = ()
    screen_overlays: tuple[ScreenOverlay, ...] = ()
    meta: dict[str, object] = field(default_factory=dict)
    world_view: ViewTransform = field(default_factory=ViewTransform)

    def layer_operations(
        self, layer: Layer | str
    ) -> tuple[DrawOperation, ...]:
        """Return prepared operations belonging to one render layer."""
        return tuple(
            operation
            for operation in self.operations
            if operation.layer == layer
        )


@dataclass(frozen=True)
class FramePacket:
    """Associate prepared scene rendering data with scene-stack metadata."""

    scene_id: str
    is_overlay: bool
    packet: RenderPacket

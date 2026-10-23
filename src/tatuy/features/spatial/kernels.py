"""Replaceable spatial kernels for performance-sensitive operations."""

from __future__ import annotations

from typing import Protocol

from tatuy.ecs.world import World
from tatuy.features.spatial.components import AttachedTo, Transform


class AttachmentKernel(Protocol):
    """Resolve attached entity transforms for one batch."""

    def update(self, world: World) -> None:
        """Update all child transforms from their parent transform and offset."""


class PythonAttachmentKernel:
    """Reference attachment processing implemented with Python ECS queries."""

    def update(self, world: World) -> None:
        """Resolve every Transform paired with AttachedTo in one batch."""
        for _, transform, attachment in world.query(Transform, AttachedTo):
            parent_transform = world.get_component(
                attachment.entity, Transform
            )
            transform.position = parent_transform.position + attachment.offset

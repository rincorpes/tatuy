"""Public bounds feature API."""

from tatuy.features.bounds.components import BoundsBehavior, BoundsConstraint
from tatuy.features.bounds.resources import (
    BoundsBounceEvent,
    BoundsFrame,
    WorldBounds,
    WorldBoundsBorder,
)
from tatuy.features.bounds.systems import (
    BoundsConstraintSystem,
    BoundsDirectionSystem,
    WorldBoundsRenderSystem,
)

__all__ = [
    "BoundsBehavior",
    "BoundsBounceEvent",
    "BoundsConstraint",
    "BoundsConstraintSystem",
    "BoundsDirectionSystem",
    "BoundsFrame",
    "WorldBounds",
    "WorldBoundsBorder",
    "WorldBoundsRenderSystem",
]

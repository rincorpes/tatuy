"""Public collision feature API."""

from tatuy.features.collision.collider_access import ColliderAccess
from tatuy.features.collision.components import (
    BoxCollider,
    CircleCollider,
    CollisionBody,
    PolygonCollider,
)
from tatuy.features.collision.match_contact import match_contact
from tatuy.features.collision.resources import CollisionContact, CollisionFrame
from tatuy.features.collision.systems import (
    CollisionDetectionSystem,
    CollisionDirectionSystem,
    CollisionResponseSystem,
)
from tatuy.features.collision.velocity_rule import (
    CollisionVelocities,
    CollisionVelocityRule,
)

__all__ = [
    "BoxCollider",
    "CircleCollider",
    "ColliderAccess",
    "CollisionBody",
    "CollisionContact",
    "CollisionDetectionSystem",
    "CollisionDirectionSystem",
    "CollisionFrame",
    "CollisionResponseSystem",
    "CollisionVelocities",
    "CollisionVelocityRule",
    "PolygonCollider",
    "match_contact",
]

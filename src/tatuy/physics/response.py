from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from tatuy.ecs.resources import CollisionContact
from tatuy.ecs.world import BaseWorld
from tatuy.math.vec2 import Vec2


@dataclass(frozen=True)
class CollisionVelocities:
    a: Vec2
    b: Vec2


class CollisionVelocityRule(ABC):
    @abstractmethod
    def resolve(
        self,
        world: BaseWorld,
        contact: CollisionContact,
    ) -> CollisionVelocities | None:
        """
        Calculate replacement velocities for this contact.

        Return None to allow another rule or the default impulse.
        Do not mutate world state.
        """

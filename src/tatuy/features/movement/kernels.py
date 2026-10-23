"""Replaceable movement kernels for performance-sensitive operations."""

from __future__ import annotations

from typing import Protocol

from tatuy.ecs.world import World
from tatuy.features.movement.components import (
    DesiredMovement,
    Movement,
    Velocity,
)
from tatuy.features.movement.motor import MovementMotor
from tatuy.features.spatial.components import Transform


class MovementCalculationKernel(Protocol):
    """Calculate entity velocities from movement intent for one step."""

    def update(self, world: World, dt: float) -> None:
        """Apply one batch movement-calculation step to a world."""


class PythonMovementCalculationKernel:
    """Reference movement calculation implemented with Python ECS queries."""

    def __init__(self, motor: MovementMotor | None = None) -> None:
        self._motor = motor or MovementMotor()

    def update(self, world: World, dt: float) -> None:
        """Update every Movement/DesiredMovement/Velocity tuple."""
        for _, movement, desired, velocity in world.query(
            Movement,
            DesiredMovement,
            Velocity,
        ):
            velocity.value = self._motor.calculate_velocity(
                current=velocity.value,
                desired=desired.direction,
                movement=movement,
                dt=dt,
            )


class VelocityIntegrationKernel(Protocol):
    """Integrate entity positions from velocity for one simulation step."""

    def integrate(self, world: World, dt: float) -> None:
        """Apply one batch velocity-integration step to a world."""


class PythonVelocityIntegrationKernel:
    """Reference velocity integration implemented with Python ECS queries."""

    def integrate(self, world: World, dt: float) -> None:
        """Update every Transform paired with Velocity using ``dt``."""
        for _, transform, velocity in world.query(Transform, Velocity):
            transform.position += velocity.value * dt

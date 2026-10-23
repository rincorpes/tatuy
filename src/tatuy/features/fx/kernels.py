"""Replaceable FX kernels for performance-sensitive particle processing."""

from __future__ import annotations

from math import exp
from typing import Protocol

from tatuy.ecs.world import World
from tatuy.features.fx.components import Particle
from tatuy.features.lifecycle.components import Lifetime
from tatuy.features.movement.components import Velocity
from tatuy.features.visual.components import Circle
from tatuy.graphics.color import ColorFormatter


class ParticleProcessingKernel(Protocol):
    """Process all active particles for one simulation step."""

    def update(self, world: World, dt: float) -> None:
        """Apply one batch particle update to the world."""


class PythonParticleProcessingKernel:
    """Reference particle processing implemented with Python ECS queries."""

    def update(self, world: World, dt: float) -> None:
        """Update particle visuals and velocity drag for all matching entities."""
        for _, particle, lifetime, circle, velocity in world.query(
            Particle,
            Lifetime,
            Circle,
            Velocity,
        ):
            fraction = max(
                0.0,
                lifetime.remaining / particle.duration,
            )

            circle.visible = fraction > 0
            circle.radius = max(1.0, particle.radius * fraction)

            red, green, blue, alpha = ColorFormatter.rgba(particle.color)
            circle.color = (
                red,
                green,
                blue,
                int(alpha * (220 / 255) * fraction),
            )

            velocity.value *= exp(-particle.drag * dt)

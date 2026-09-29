from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, sin
from random import Random

from tatuy.ecs.entity import EntityId
from tatuy.ecs.entity.factory import (
    CircleBlueprint,
    CircleBlueprintAttrs,
    EntityFactory,
)
from tatuy.ecs.world import TWorld
from tatuy.features.fx.components import Particle
from tatuy.features.lifecycle.components import Lifetime
from tatuy.features.movement.components import Velocity
from tatuy.features.visual.components import Circle
from tatuy.graphics.color import Color, ColorFormatter
from tatuy.math.vec2 import Vec2


class ParticlesFactory(EntityFactory): ...


@dataclass(frozen=True, kw_only=True)
class ParticleBlueprintAttrs(CircleBlueprintAttrs):
    velocity: Vec2
    lifetime: float
    drag: float = 4.0


@ParticlesFactory.blueprint("particle")
class ParticleBlueprint(CircleBlueprint[TWorld]):
    attrs_type = ParticleBlueprintAttrs

    def compose(self, attrs: ParticleBlueprintAttrs):
        return (
            Velocity(attrs.velocity),
            Lifetime(attrs.lifetime),
            Particle(
                duration=attrs.lifetime,
                radius=attrs.radius,
                color=attrs.color,
                drag=attrs.drag,
            ),
        )


@dataclass(frozen=True)
class ParticleBurst:
    count: int = 10

    speed_min: float = 45.0
    speed_max: float = 150.0

    lifetime_min: float = 0.25
    lifetime_max: float = 0.5

    radius_min: float = 2.0
    radius_max: float = 4.0

    drag: float = 4.0

    z: int = 5

    def __post_init__(self):
        if not 0 < self.lifetime_min <= self.lifetime_max:
            raise ValueError(
                "ParticleBurst requires " "0 < lifetime_min <= lifetime_max"
            )


class ParticleEmitter:
    def __init__(
        self,
        world: TWorld,
        *,
        rng: Random | None = None,
        max_particles: int = 500,
    ):
        self._world = world
        self._factory = ParticlesFactory(world)
        self._rng = rng or Random()
        self._max_particles = max_particles

    def emit(
        self,
        position: Vec2,
        color: Color,
        burst: ParticleBurst,
    ) -> tuple[EntityId, ...]:

        available = self._max_particles - sum(
            1 for _ in self._world.query(Particle)
        )

        count = min(burst.count, available)

        entities = []

        for _ in range(max(0, count)):
            angle = self._rng.uniform(0, 2 * pi)
            speed = self._rng.uniform(
                burst.speed_min,
                burst.speed_max,
            )

            entity = self._factory.create(
                name="particle",
                position=Vec2(position.x, position.y),
                velocity=Vec2(cos(angle), sin(angle)) * speed,
                radius=self._rng.uniform(
                    burst.radius_min,
                    burst.radius_max,
                ),
                color=color,
                lifetime=self._rng.uniform(
                    burst.lifetime_min,
                    burst.lifetime_max,
                ),
                drag=burst.drag,
            )

            circle = self._world.get_component(entity, Circle)
            circle.z = burst.z

            r, g, b, alpha = ColorFormatter.rgba(color)
            circle.color = (
                r,
                g,
                b,
                int(alpha * (220 / 255)),
            )
            entities.append(entity)

        return tuple(entities)

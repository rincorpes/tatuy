from __future__ import annotations

from math import exp

from tatuy.ecs.system import BaseSystem, SystemPhase
from tatuy.ecs.world import TWorld
from tatuy.features.fx.components import Particle, Trail, TrailPoint
from tatuy.features.lifecycle.components import Lifetime
from tatuy.features.movement.components import Velocity
from tatuy.features.spatial.components import Transform
from tatuy.features.visual.components import Circle
from tatuy.graphics.color import ColorFormatter
from tatuy.math.vec2 import Vec2
from tatuy.scenes.context import SceneTickContext, TContext, TIntent


class ParticleUpdateSystem(BaseSystem[TContext]):
    def step(self, ctx: SceneTickContext[TWorld, TIntent]):
        for _, particle, lifetime, circle, velocity in ctx.world.query(
            Particle, Lifetime, Circle, Velocity
        ):
            fraction = max(
                0.0,
                lifetime.remaining / particle.duration,
            )

            circle.visible = fraction > 0
            circle.radius = max(1.0, particle.radius * fraction)

            r, g, b, alpha = ColorFormatter.rgba(particle.color)
            circle.color = (
                r,
                g,
                b,
                int(alpha * (220 / 255) * fraction),
            )

            velocity.value *= exp(-particle.drag * ctx.dt)


class TrailSystem(BaseSystem[TContext]):
    def step(self, ctx: SceneTickContext[TWorld, TIntent]):
        for _, trail, transform in ctx.world.query(
            Trail,
            Transform,
        ):
            self._age(trail, ctx.dt)

            if not trail.enabled:
                continue

            trail.clock += ctx.dt

            if trail.clock < trail.interval:
                continue

            trail.clock %= trail.interval

            trail.points.append(
                TrailPoint(
                    position=Vec2(
                        transform.position.x,
                        transform.position.y,
                    ),
                    radius=trail.radius,
                    color=trail.color,
                )
            )

            while len(trail.points) > trail.max_points:
                trail.points.popleft()

    def _age(self, trail: Trail, dt: float):
        for point in trail.points:
            point.age += dt

        while trail.points and trail.points[0].age >= trail.duration:
            trail.points.popleft()


class TrailRenderSystem(BaseSystem[TContext]):
    phase = SystemPhase.PRESENTATION

    def step(self, ctx: SceneTickContext[TWorld, TIntent]):
        for _, trail in ctx.world.query(Trail):
            for point in trail.points:
                fade = max(
                    0.0,
                    1 - point.age / trail.duration,
                )

                ctx.render_queue.circle(
                    center=point.position,
                    radius=max(
                        1.0,
                        point.radius * (0.3 + 0.7 * fade),
                    ),
                    color=(
                        *point.color[:3],
                        int(110 * fade * fade),
                    ),
                    layer="world",
                    z=-5,
                )

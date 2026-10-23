from random import Random
from types import SimpleNamespace

import pytest

from tatuy.ecs.world import World
from tatuy.features.fx.components import Particle, Trail, TrailPoint
from tatuy.features.fx.particles import ParticleBurst, ParticleEmitter
from tatuy.features.fx.systems import TrailRenderSystem, TrailSystem
from tatuy.features.spatial.components import Transform
from tatuy.graphics.render.queue import RenderQueue
from tatuy.math.vec2 import Vec2


def test_particle_emitter_is_deterministic_with_injected_rng():
    def emit(seed: int):
        world = World()
        result = ParticleEmitter(
            world, rng=Random(seed), max_particles=10
        ).emit(
            Vec2(10.0, 20.0),
            (100, 110, 120),
            ParticleBurst(
                count=2,
                speed_min=5.0,
                speed_max=5.0,
                lifetime_min=1.0,
                lifetime_max=1.0,
                radius_min=2.0,
                radius_max=2.0,
            ),
        )
        return [
            (
                world.get_component(entity, Transform).position,
                world.get_component(entity, Particle).duration,
            )
            for entity in result.entities
        ]

    assert emit(1234) == emit(1234)


def test_particle_emitter_respects_capacity():
    world = World()
    emitter = ParticleEmitter(world, rng=Random(1), max_particles=2)

    result = emitter.emit(
        Vec2.zero(),
        (255, 255, 255),
        ParticleBurst(count=5),
    )

    assert result.requested == 5
    assert result.emitted == 2
    assert result.available == 2
    assert emitter.available == 0


def test_trail_system_ages_expires_and_caps_points():
    world = World()
    entity = world.create_entity()
    trail = world.add_component(
        entity,
        Trail(duration=0.5, interval=0.1, max_points=2),
    )
    transform = world.add_component(entity, Transform(Vec2(1.0, 2.0)))
    trail.points.append(TrailPoint(Vec2.zero(), 1.0, (1, 2, 3), age=0.45))

    system = TrailSystem()
    system.step(SimpleNamespace(world=world, dt=0.1))
    transform.position = Vec2(3.0, 4.0)
    system.step(SimpleNamespace(world=world, dt=0.1))
    transform.position = Vec2(5.0, 6.0)
    system.step(SimpleNamespace(world=world, dt=0.1))

    assert len(trail.points) == 2
    assert [point.position for point in trail.points] == [
        Vec2(3.0, 4.0),
        Vec2(5.0, 6.0),
    ]


def test_trail_render_system_submits_faded_world_circles():
    world = World()
    entity = world.create_entity()
    trail = world.add_component(entity, Trail(duration=1.0))
    trail.points.append(
        TrailPoint(Vec2(2.0, 3.0), 10.0, (10, 20, 30), age=0.5)
    )
    queue = RenderQueue()

    TrailRenderSystem().step(SimpleNamespace(world=world, render_queue=queue))

    ops = queue.iter_sorted()
    assert len(ops) == 1
    assert ops[0].layer == "world"
    assert ops[0].z == -5
    assert ops[0].payload.center == Vec2(2.0, 3.0)
    assert ops[0].payload.radius == pytest.approx(6.5)
    assert ops[0].payload.color == (10, 20, 30, 27)

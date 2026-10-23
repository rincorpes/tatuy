from dataclasses import dataclass
from types import SimpleNamespace

from tatuy.ecs.entity.factory import EntityBlueprint, EntityFactory
from tatuy.ecs.world import World
from tatuy.features.lifecycle.commit import LifecycleCommitter
from tatuy.features.lifecycle.components import (
    DespawnReason,
    Lifetime,
    Respawn,
    SpawnOrigin,
)
from tatuy.features.lifecycle.kernels import PythonLifecycleCommitKernel
from tatuy.features.lifecycle.resources import (
    LifecycleQueue,
    SpawnDefinition,
    SpawnRegistry,
)


@dataclass
class Marker:
    value: int


class MarkerBlueprint(EntityBlueprint[World]):
    def build(self, world, entity, **kwargs):
        world.add_component(entity, Marker(kwargs["value"]))


class LifecycleFactory(EntityFactory):
    registry = {"marker": MarkerBlueprint}


def _world_with_lifecycle() -> World:
    world = World()
    world.add_resource(LifecycleQueue())
    world.add_resource(SpawnRegistry())
    return world


def test_python_kernel_spawns_with_overrides_and_lifecycle_metadata():
    world = _world_with_lifecycle()
    factory = LifecycleFactory(world)
    registry = world.get_resource(SpawnRegistry)
    registry.definitions["enemy"] = SpawnDefinition(
        blueprint="marker",
        make_kwargs=lambda: {"value": 1},
        respawn=Respawn(delay=3.0),
        lifetime=5.0,
    )
    world.get_resource(LifecycleQueue).request_spawn(
        "enemy",
        kwargs={"value": 7},
    )

    PythonLifecycleCommitKernel().commit(world, factory)

    entities = list(world.entities)
    assert len(entities) == 1
    entity = entities[0]
    assert world.get_component(entity, Marker).value == 7
    assert world.get_component(entity, SpawnOrigin).definition == "enemy"
    assert world.get_component(entity, Respawn).delay == 3.0
    assert world.get_component(entity, Lifetime).remaining == 5.0


def test_python_kernel_despawn_queues_respawn_when_policy_allows():
    world = _world_with_lifecycle()
    factory = LifecycleFactory(world)
    entity = world.create_entity()
    world.add_component(entity, SpawnOrigin(definition="enemy"))
    world.add_component(
        entity,
        Respawn(
            delay=1.5,
            reasons=frozenset({DespawnReason.DEFEATED}),
        ),
    )
    queue = world.get_resource(LifecycleQueue)
    queue.request_despawn(entity, DespawnReason.DEFEATED)

    PythonLifecycleCommitKernel().commit(world, factory)

    assert entity not in world.entities
    assert len(queue.spawns) == 1
    assert queue.spawns[0].definition == "enemy"
    assert queue.spawns[0].remaining == 1.5


def test_python_kernel_without_lifecycle_queue_is_noop():
    world = World()
    factory = LifecycleFactory(world)

    PythonLifecycleCommitKernel().commit(world, factory)

    assert list(world.entities) == []


def test_committer_delegates_one_batch_call_to_injected_kernel():
    world = World()
    factory = LifecycleFactory(world)
    calls = []

    class RecordingKernel:
        def commit(self, kernel_world, kernel_factory):
            calls.append((kernel_world, kernel_factory))

    committer = LifecycleCommitter(factory, kernel=RecordingKernel())
    ctx = SimpleNamespace(world=world)

    committer.commit(ctx)

    assert calls == [(world, factory)]

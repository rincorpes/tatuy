from types import SimpleNamespace

from tatuy.ecs.world import World
from tatuy.features.lifecycle.components import DespawnReason, Lifetime
from tatuy.features.lifecycle.resources import LifecycleQueue
from tatuy.features.lifecycle.systems import LifetimeSystem, SpawnDelaySystem


def test_spawn_delay_system_advances_pending_requests_without_going_negative():
    world = World()
    queue = world.add_resource(LifecycleQueue())
    queue.request_spawn("enemy", delay=1.0)

    SpawnDelaySystem().step(SimpleNamespace(world=world, dt=1.5))

    assert queue.spawns[0].remaining == 0.0


def test_lifetime_system_decrements_and_requests_despawn_when_expired():
    world = World()
    queue = world.add_resource(LifecycleQueue())
    entity = world.create_entity()
    lifetime = world.add_component(entity, Lifetime(remaining=0.25))

    LifetimeSystem().step(SimpleNamespace(world=world, dt=0.5))

    assert lifetime.remaining == -0.25
    assert queue.despawns[entity].reason is DespawnReason.LIFETIME_EXPIRED


def test_lifecycle_queue_batches_ready_spawns_and_preserves_waiting_spawns():
    queue = LifecycleQueue()
    queue.request_spawn("ready")
    queue.request_spawn("waiting", delay=1.0)

    batch = queue.take_ready_batch()

    assert [request.definition for request in batch.spawns] == ["ready"]
    assert [request.definition for request in queue.spawns] == ["waiting"]


def test_lifecycle_queue_first_despawn_request_wins():
    queue = LifecycleQueue()
    entity = 1

    queue.request_despawn(entity, DespawnReason.DEFEATED)
    queue.request_despawn(entity, DespawnReason.OUT_OF_BOUNDS)

    assert queue.despawns[entity].reason is DespawnReason.DEFEATED


def test_permanent_despawn_overrides_respawn_allowed_request():
    queue = LifecycleQueue()
    entity = 1

    queue.request_despawn(entity, DespawnReason.DEFEATED)
    queue.request_despawn(
        entity,
        DespawnReason.OUT_OF_BOUNDS,
        allow_respawn=False,
    )

    request = queue.despawns[entity]
    assert request.reason is DespawnReason.OUT_OF_BOUNDS
    assert request.allow_respawn is False

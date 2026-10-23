# Spawning and Lifecycle

Tatuy treats entity creation/destruction as structured lifecycle work rather than requiring arbitrary immediate mutation from game systems.

## Spawn definitions

A `SpawnDefinition` names a reusable blueprint plus optional construction policy:

```python
SpawnDefinition(
    blueprint="enemy",
    make_kwargs=lambda: {"lane": 2},
    lifetime=8.0,
    respawn=Respawn(delay=1.0),
)
```

A scene exposes definitions through `spawn_definitions()` and initial placements through `entities()`.

Runtime composition validates those declarations, creates the spawn registry/queue, and schedules initial spawns before `on_enter()`.

## Runtime spawning

Game systems request future creation through `LifecycleQueue`:

```python
queue.request_spawn("enemy", delay=0.5)
```

Requests may override or extend default blueprint kwargs.

`SpawnDelaySystem` advances delayed requests. Ready work is committed at structural barriers rather than mutating the world during arbitrary system iteration.

## Despawning

A despawn request records:

- entity
- `DespawnReason`
- whether respawn is allowed

The first request for an entity normally wins. An explicit permanent removal (`allow_respawn=False`) overrides an earlier request that allowed respawn.

Common reasons include:

- `OUT_OF_BOUNDS`
- `LIFETIME_EXPIRED`
- `DEFEATED`
- `SCRIPTED`

## Lifetime

A `Lifetime` component stores remaining lifetime. `LifetimeSystem` decrements it after simulation and requests `LIFETIME_EXPIRED` when it reaches zero.

## Respawn

Entities created from a spawn definition carry their spawn origin. If that definition has a `Respawn` policy and the despawn reason is allowed, lifecycle commit can queue a replacement after the configured delay.

Respawn therefore depends on declaration-time origin plus runtime despawn reason; game code does not reconstruct the entity manually.

## Ordering contract

Default lifecycle behavior is distributed across the frame intentionally:

```text
PRE_SIMULATION
    SpawnDelaySystem

POST_SIMULATION
    LifetimeSystem

structural commit barriers
    apply ready spawn/despawn work
```

This keeps entity-set mutation outside normal iteration-sensitive simulation work.

## What is implementation detail?

Normal game code should not install `SpawnSystem`/`DespawnSystem` manually or depend on lifecycle committer internals. The runtime owns default lifecycle commit plumbing.

## Native preservation contract

A replacement implementation must preserve:

- spawn-definition meaning and validation
- delayed spawn timing
- queue batching semantics
- first-request-wins despawn behavior
- permanent-removal override behavior
- lifetime expiration reason
- respawn reason filtering and delay
- structural-barrier timing visible to game systems

## Examples

- `examples/fundamentals/013_lifecycle/001_lifetime/app.py`
- `examples/fundamentals/013_lifecycle/002_respawn/app.py`
- `examples/fundamentals/013_lifecycle/003_runtime_spawn_queue/app.py`

See [Create a spawn definition](../guides/create-a-spawn-definition.md).

---
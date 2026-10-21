# Spawning and Lifecycle

Tatuy uses lifecycle requests rather than requiring game systems to create and destroy entities immediately.

## Spawn definitions

```python
SpawnDefinition(
    "enemy",
    make_kwargs=lambda: {...},
)
```

A definition describes:

- blueprint
- default kwargs
- optional respawn policy
- optional lifetime

## Spawn registry

Scenes register definitions by game-facing name:

```text
"enemy"
"player"
"ball"
```

## Spawn requests

Systems request:

```text
spawn "enemy"
```

rather than reconstructing its blueprint every time.

## Lifecycle queue

Requests wait in `LifecycleQueue`.

They are committed at structural barriers.

## Despawning

A despawn request records:

- entity
- reason
- whether respawn is allowed

## Lifetime

A `Lifetime` component allows generic expiration.

## Respawn

Entities created from a spawn definition can remember their origin.

If the entity has a matching respawn policy when despawned, the lifecycle system can queue a replacement.

---

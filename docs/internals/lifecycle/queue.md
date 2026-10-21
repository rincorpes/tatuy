# LifecycleQueue Internals

The lifecycle queue stores:

```text
spawns: list[SpawnRequest]
despawns: dict[EntityId, DespawnRequest]
```

Spawn requests may have remaining delay.

`advance_spawn_delays()` decrements pending delays.

`take_ready_batch()` separates ready spawns from waiting spawns and consumes the current despawn batch.

---

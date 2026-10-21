# LifecycleCommitter Internals

The lifecycle committer applies ready spawn/despawn work.

Spawn flow:

```text
definition lookup
    ↓
build default kwargs
    ↓
merge request kwargs
    ↓
factory.create()
    ↓
SpawnOrigin
    ↓
optional Respawn
    ↓
optional Lifetime
```

Despawn flow:

```text
validate entity
    ↓
check respawn policy
    ↓
queue replacement if applicable
    ↓
destroy entity
```

The committer also records profiler metrics for spawn preparation, factory work, and metadata application.

---

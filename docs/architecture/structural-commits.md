# Structural Commits

Tatuy separates ordinary simulation from changes to ECS structure.

Examples of structural work:

```text
create entity
destroy entity
add component type
remove component type
```

## Barriers

```text
PRE_SIMULATION
    ↓
PRE_SIM_COMMIT
    ↓
SIMULATION
    ↓
POST_SIMULATION
    ↓
POST_SIM_COMMIT
```

## SceneStructuralCommitter

The scene committer currently combines:

```text
StructuralCommandBuffer
LifecycleCommitter
```

The first handles queued component-structure operations.

The second handles entity lifecycle.

## Why?

Systems should be able to iterate over the world without arbitrary mid-query changes making execution dependent on storage details.

The semantic contract is:

```text
request change
    ↓
continue current phase
    ↓
known barrier
    ↓
apply change
```

---

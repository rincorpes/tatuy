# System Pipeline Architecture

Tatuy uses explicit phases because simulation ordering matters.

```text
CONTROL
    ↓
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

Presentation runs separately.

## Registrations become scheduled steps

A registration contains:

```text
system
optional phase override
optional order override
optional activation predicate
```

A `BaseSystem` normally creates one step.

A `GameSystem` may create one step per implemented phase callback.

## Why phase + order?

Phase communicates semantic location.

Order resolves sequencing inside that location.

This is easier to understand than one global list of arbitrary numeric priorities.

## Default built-in composition

`tatuy.engine.runtime.builtins.BuiltinSystemCatalog` is the intentional composition root for Tatuy's default feature systems. Runtime composition may depend on concrete built-in features here because deciding what is installed, when it is active, and how it is ordered is a runtime responsibility.

Activation predicates are intentionally coarse. They check cheap prerequisites such as required resources, the presence of a relevant entity, or whether a per-frame event list contains work. Detailed entity validation and feature behavior remain owned by the feature system/kernel instead of being duplicated in activation code.

The default schedule is:

| Phase | System | Order |
| --- | --- | ---: |
| `CONTROL` | `MovementControlSystem` | 0 |
| `PRE_SIMULATION` | `SpawnDelaySystem` | -1000 |
| `PRE_SIMULATION` | `MotionSnapshotSystem` | 100 |
| `PRE_SIMULATION` | `MovementSystem` | 200 |
| `SIMULATION` | `VelocityIntegrationSystem` | 100 |
| `SIMULATION` | `BoundsConstraintSystem` | 200 |
| `SIMULATION` | `AttachmentSystem` | 300 |
| `SIMULATION` | `CollisionDetectionSystem` | 400 |
| `SIMULATION` | `CollisionResponseSystem` | 500 |
| `POST_SIMULATION` | `BoundsDirectionSystem` | 0 |
| `POST_SIMULATION` | `CollisionDirectionSystem` | 0 |
| `POST_SIMULATION` | `LifetimeSystem` | 1000 |
| `PRESENTATION` | `RenderSystem` | 0 |
| `PRESENTATION` | `UiRenderSystem` | 0 |
| `PRESENTATION` | `WorldBoundsRenderSystem` | 0 |

Order values are guarantees within a phase. Systems with the same order are deterministically sorted by system name and then registration sequence; callers should not create semantic dependencies on same-order tie-breaking. If a dependency matters, give it an explicit order.

In particular, collision direction synchronization is post-simulation work: it observes contacts after collision detection and response rather than consuming the previous frame's contact data.

## Diagnostics

Scheduled steps track their latest state.

This allows the pipeline to expose whether a system:

- did not apply
- was disabled
- ran
- failed

The goal is inspectable execution.

---

# Kernel Boundaries

Tatuy keeps gameplay orchestration in Python while allowing performance-sensitive engine work to move behind replaceable kernels.

## Rule

A system may delegate a hot path to a kernel, but the Python/native boundary should be coarse-grained. Do not cross the boundary once per entity or component.

The preferred shape is:

```text
Game/System pipeline
    ↓ one call per phase/subsystem
System
    ↓ one batch call
Kernel contract
    ├── Python reference implementation
    └── future native implementation
```

Game code depends on the system and normal Tatuy components. It should not select storage layouts, native handles, or binding details.

## Velocity integration

`VelocityIntegrationSystem` is the first kernelized subsystem.

```text
VelocityIntegrationSystem.step(ctx)
    ↓
VelocityIntegrationKernel.integrate(world, dt)
    ↓
PythonVelocityIntegrationKernel
    ↓
World.query(Transform, Velocity)
```

The system owns simulation-phase scheduling. The kernel owns the batch operation that updates matching entities.

The Python implementation is the reference behavior. A future native implementation must preserve the same observable results while being free to use a native-backed ECS or another internal representation.

## Movement calculation

`MovementSystem` delegates movement calculation as one batch operation while preserving `MovementMotor` as the scalar/reference calculation helper.

```text
MovementSystem.step(ctx)
    ↓
MovementCalculationKernel.update(world, dt)
    ↓
PythonMovementCalculationKernel
    ↓
World.query(Movement, DesiredMovement, Velocity)
    ↓ per matching entity
MovementMotor.calculate_velocity(...)
```

The system owns pre-simulation scheduling. The kernel owns iteration over matching entities. `MovementMotor` remains reusable Python policy inside the reference kernel and can continue to be injected for custom calculation behavior.

A future native movement kernel may replace the entire Python batch path without changing game code or `MovementSystem` usage.

## Bounds constraints

`BoundsConstraintSystem` delegates bounds processing as one batch operation. The Python reference kernel owns collider lookup plus clamp, bounce, wrap, and despawn constraint application.

```text
BoundsConstraintSystem.step(ctx)
    ↓
BoundsConstraintKernel.apply(world)
    ↓
PythonBoundsConstraintKernel
    ↓
World.query(BoundsConstraint, Transform)
```

`BoundsDirectionSystem` remains outside the kernel because it consumes bounce events to update higher-level movement intent. That post-simulation policy should remain in Python unless profiling later proves it belongs in a native batch operation.

## Spatial attachments

`AttachmentSystem` uses a separate spatial kernel rather than sharing the bounds kernel.

```text
AttachmentSystem.step(ctx)
    ↓
AttachmentKernel.update(world)
    ↓
PythonAttachmentKernel
    ↓
World.query(Transform, AttachedTo)
```

Bounds and spatial operations are intentionally separate contracts because they own different data, behavior, and future native implementation concerns.

## Collision detection

`CollisionDetectionSystem` delegates the full broad-phase-like collection and pair-testing pass as one batch operation. The Python reference kernel owns collider collection, deterministic entity ordering, pair generation, geometric contact tests, `CollisionFrame` population, and detection metrics.

```text
CollisionDetectionSystem.step(ctx)
    ↓
CollisionDetectionKernel.detect(world)
    ↓
PythonCollisionDetectionKernel
    ├── collect colliders
    ├── sort by EntityId
    ├── test collider pairs
    └── populate CollisionFrame
```

Detection remains separate from `CollisionResponseSystem`. Sensors still produce contacts during detection; response decides whether a contact should produce physical separation or velocity changes.

## Collision response

`CollisionResponseSystem` delegates contact resolution as one batch operation.

```text
CollisionResponseSystem.step(ctx)
    ↓
CollisionResponseKernel.respond(world)
    ↓
PythonCollisionResponseKernel
    ├── filter incomplete/sensor/immovable contacts
    ├── correct penetration
    ├── apply Python CollisionVelocityRule overrides when configured
    └── otherwise apply the default impulse response
```

The Python reference kernel preserves the existing `CollisionVelocityRule` extension point and its timing: rules run only after the contact is eligible, penetration has been corrected, and the bodies are still approaching.

System-level Python velocity rules are only valid with the default Python response kernel. A custom/native response kernel must own any custom response policy itself; Tatuy does not design the native boundary around per-contact Python callbacks.

`CollisionDirectionSystem` remains outside the kernel because it translates resulting velocity back into higher-level movement intent.

## Lifecycle bulk commits

`LifecycleCommitter` remains the structural-barrier orchestration object, but delegates the ready lifecycle batch as one operation.

```text
LifecycleCommitter.commit(ctx)
    ↓
LifecycleCommitKernel.commit(world, factory)
    ↓
PythonLifecycleCommitKernel
    ├── take the ready LifecycleQueue batch
    ├── apply despawns and respawn policy
    ├── resolve SpawnRegistry definitions
    ├── call EntityFactory for Python blueprint spawns
    └── attach lifecycle metadata
```

The default Python kernel preserves arbitrary Python blueprint construction. That factory path is an explicit Python extension point rather than a requirement that a future native kernel call back into Python once per spawned entity.

A future native lifecycle implementation may batch native-known creation/destruction while falling back to the Python reference path for blueprint-driven spawns. Game code and the structural commit barrier continue to depend on `LifecycleCommitter`, not on native storage or handles.

## Particle processing

`ParticleUpdateSystem` delegates per-frame particle visual/drag updates as one batch operation.

```text
ParticleUpdateSystem.step(ctx)
    ↓
ParticleProcessingKernel.update(world, dt)
    ↓
PythonParticleProcessingKernel
    └── World.query(Particle, Lifetime, Circle, Velocity)
```

The reference kernel preserves the existing lifetime fraction, visibility, radius, alpha fade, and exponential drag behavior. `ParticleEmitter` remains in Python because burst configuration, randomness, and blueprint-driven entity creation are authoring/creation policy rather than the hot per-frame processing loop.

Trail update/render systems remain separate. They own different data and rendering policy and should only receive their own kernel boundary if profiling later justifies it.

## Kernel requirements

Each kernelized subsystem should:

- expose a small operation-oriented contract
- receive the whole batch/context needed for one operation
- keep scheduling and gameplay policy outside the kernel
- provide a Python reference implementation
- have behavior/conformance tests independent of the concrete implementation
- keep native bindings and storage details out of game-facing APIs

Do not introduce a native implementation until the Python contract and tests are stable.

---

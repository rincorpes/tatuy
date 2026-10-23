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

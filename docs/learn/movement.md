# Movement

Tatuy separates player intent, desired movement, velocity generation, and spatial integration.

## Low-level velocity integration

At the lowest level:

```text
Transform
+
Velocity
    ↓
VelocityIntegrationSystem
```

`VelocityIntegrationSystem` advances `Transform.position` from velocity and frame `dt`.

## Desired movement

Higher-level movement uses:

```text
MovementControls
DesiredMovement
Movement
Velocity
Transform
```

Conceptually:

```text
input / game intent
        ↓
MovementControlSystem
        ↓
DesiredMovement
        ↓
MovementSystem
        ↓
Velocity
        ↓
VelocityIntegrationSystem
        ↓
Transform
```

This separates control mapping from movement behavior and final spatial integration.

## Movement contract

`Movement` owns tuning such as speed, acceleration, deceleration, and maximum speed. `MovementSystem` uses desired direction plus the current velocity to produce the next velocity.

When controls request normalized movement, diagonal input is normalized before speed is applied.

Zero desired direction allows the movement model to decelerate instead of forcing velocity to zero immediately.

## Motion snapshots

`MotionSnapshotSystem` records previous position before simulation advances the transform. Features that need the previous position can use the snapshot rather than reconstructing it after movement.

## Built-in activation

Normal scenes do not manually install movement built-ins. Runtime composition activates them when the required component combinations exist.

Default placement is:

```text
CONTROL
    MovementControlSystem
PRE_SIMULATION
    MotionSnapshotSystem
    MovementSystem
SIMULATION
    VelocityIntegrationSystem
```

## What is implementation detail?

Game code should not depend on the current Python movement kernel implementation or runtime activation predicate implementation.

## Native preservation contract

A native movement kernel must preserve:

- desired-direction interpretation
- normalization behavior
- acceleration/deceleration semantics
- maximum-speed clamping
- velocity integration against `dt`
- motion snapshot timing
- built-in phase/order behavior

## Examples

- `examples/fundamentals/010_movement/001_velocity_integration/app.py`
- `examples/fundamentals/010_movement/002_movement_system/app.py`
- `examples/fundamentals/010_movement/003_controlled_movement/app.py`

---
# Collisions

Tatuy separates collision geometry, contact detection, generic physical response, and game meaning.

## Public collision model

Use public collision components/resources such as:

```python
from tatuy.features.collision import (
    BoxCollider,
    CircleCollider,
    CollisionBody,
    CollisionFrame,
    ColliderAccess,
    PolygonCollider,
)
```

Colliders describe shape and sensor state. `CollisionBody` describes generic response properties such as inverse mass and restitution.

## Detection

The built-in collision detection system observes entities that have a collider and transform, then writes contacts into `CollisionFrame`.

```text
Transform + Collider
        ↓
collision geometry
        ↓
CollisionFrame.contacts
```

Game systems can inspect the frame after detection rather than re-running geometric tests themselves.

## Physical response

Entities with `CollisionBody` may participate in generic collision response. Response uses the detected contacts and updates motion according to body state and configured velocity rules.

Detection and response remain separate so sensors and gameplay-only contacts do not need to produce physical impulses.

## Sensors and triggers

A collider with `is_sensor=True` still participates in detection but does not receive generic physical response.

Sensors are appropriate for:

- pickups
- checkpoints
- damage volumes
- trigger regions
- score/wave logic

Game code reads the contact frame and decides what the contact means.

## Custom velocity rules

`CollisionVelocityRule` is a supported extension point for contacts whose velocity response differs from Tatuy's generic impulse.

Rules are evaluated in order. A rule returning replacement velocities handles the contact; returning `None` allows the next rule or the default response to run.

Rules calculate velocities without mutating world state directly. The response system remains responsible for applying the result.

## Ordering contract

Default collision work runs in this order:

```text
SIMULATION
    CollisionDetectionSystem
    CollisionResponseSystem

POST_SIMULATION
    CollisionDirectionSystem
```

Direction synchronization therefore observes the current frame's resolved collision result.

## What is implementation detail?

Game code should not depend on the current broadphase/narrowphase implementation, contact-storage representation, or Python kernel implementation.

Geometry functions remain backend-agnostic and do not require ECS state.

## Native preservation contract

A native collision implementation must preserve:

- supported collider geometry and contact meaning
- sensor detection without physical response
- `CollisionFrame` behavior visible to game systems
- response ordering and restitution/inverse-mass semantics
- ordered custom velocity-rule behavior
- direction synchronization after current-frame response

## Examples

- `examples/fundamentals/011_collisions/001_detection/app.py`
- `examples/fundamentals/011_collisions/002_response/app.py`
- `examples/fundamentals/011_collisions/003_sensors/app.py`
- `examples/fundamentals/011_collisions/004_custom_response_rule/app.py`

See [Use collisions](../guides/use-collisions.md).

---
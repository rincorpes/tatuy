# ECS

Tatuy uses an Entity Component System.

```text
Entity
    identity

Component
    per-entity state

System
    behavior

Resource
    scene-wide state
```

## Entities

An entity is an identifier.

Its meaning comes from its components.

```text
Entity 17
├── Transform
├── Velocity
├── Circle
├── CircleCollider
└── CollisionBody
```

## Components

Components hold state.

Examples:

- `Transform`
- `Velocity`
- `Movement`
- `CollisionBody`
- `CircleCollider`
- `Rect`
- `Text`
- `Lifetime`

## Systems

Systems query useful combinations:

```python
for entity, transform, velocity in ctx.world.query(
    Transform,
    Velocity,
):
    ...
```

## Resources

Resources store world-wide state:

```python
score = ctx.world.get_resource(Score)
```

Examples:

- score
- wave state
- collision frame
- lifecycle queue
- settings

## World

```text
World
├── entities
├── component stores
└── resources
```

## Composition

Adding components opts entities into behavior.

```text
Transform + Velocity
        ↓
velocity integration

Transform + visual component
        ↓
rendering
```

This is one of Tatuy's central design patterns.

---

# Entities and Components

Entities are IDs.

Components are data attached to those IDs.

## Entity construction

Tatuy uses entity blueprints and factories.

```text
EntityFactory
     ↓
EntityBlueprint
     ↓
create entity
     ↓
attach components
```

## Blueprint

An `EntityBlueprint` describes how one entity recipe is assembled.

Tatuy includes reusable blueprints for:

- rectangles
- circles
- polygons
- text

Games can define their own.

## Factory

An `EntityFactory` maps names to blueprints.

```python
class GameFactory(EntityFactory):
    registry = {
        "rect": RectBlueprint,
    }
```

## Typed blueprints

Typed blueprints can construct an attrs dataclass from keyword arguments and compose components from it.

This is useful when a game wants reusable, validated entity recipes.

## Identity components

A blueprint may optionally attach an identity component.

That lets systems express semantic queries such as:

```text
Enemy + Transform
Ball + Velocity
Player + Health
```

without turning the entity into a class hierarchy.

## Keep components small

Prefer state:

```text
Health
Velocity
Enemy
Poisoned
```

over giant components that own entire subsystems of behavior.

---

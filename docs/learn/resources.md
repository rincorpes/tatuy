# Resources

Resources are values stored once per world by type.

They are useful for state that belongs to a scene rather than one entity.

Examples:

```text
Score
Waves
CollisionFrame
LifecycleQueue
GameSettings
```

## Adding scene resources

```python
def resources(self, ctx):
    return (
        Score(),
        Waves(...),
    )
```

## Reading resources

```python
score = ctx.world.get_resource(Score)
```

## Shared resources

Application-level values can be copied into scene worlds through:

```python
shared_resource_types = (
    GameSettings,
)
```

This is useful for settings shared by multiple scenes.

## Resource or component?

Use a component when the state belongs to an entity.

Use a resource when the state belongs to the world/scene as a whole.

---

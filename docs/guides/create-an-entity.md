# Create an Entity

For reusable gameplay entities, prefer the factory/lifecycle path.

1. Define or reuse a blueprint.
2. Register it in your factory.
3. Create a `SpawnDefinition`.
4. Request it through the lifecycle system.

Example factory:

```python
class GameFactory(EntityFactory):
    registry = {
        "circle": CircleBlueprint,
    }
```

Definition:

```python
"ball": SpawnDefinition(
    "circle",
    make_kwargs=lambda: {
        "position": Vec2(100, 100),
        "radius": 8,
    },
)
```

Initial placement:

```python
yield EntitySpawn("ball")
```

Runtime systems should generally request spawning through `LifecycleQueue`.

---

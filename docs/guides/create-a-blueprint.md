# Create a Blueprint

Use a custom blueprint when an entity requires game-specific component composition.

```python
class EnemyBlueprint(EntityBlueprint[GameWorld]):
    def build(self, world, entity, **kwargs):
        world.add_component(entity, Enemy())
        world.add_component(
            entity,
            Transform(kwargs["position"]),
        )
```

Register it:

```python
class GameFactory(EntityFactory):
    registry = {
        "enemy": EnemyBlueprint,
    }
```

Prefer typed blueprint attributes when construction has many validated fields.

Keep the blueprint focused on assembly.

Game behavior belongs in systems.

---

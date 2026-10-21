# Create a Spawn Definition

A spawn definition gives gameplay a stable name for an entity recipe.

```python
def spawn_definitions(self, ctx):
    return {
        "enemy": SpawnDefinition(
            "enemy",
            make_kwargs=lambda: {
                "position": random_position(),
            },
        ),
    }
```

The first argument is the factory blueprint name.

`make_kwargs` creates default arguments for each spawn.

Individual spawn requests may override those values.

Definitions may also carry lifetime and respawn policy.

---

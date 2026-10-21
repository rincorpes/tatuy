# Use Resources

Create a resource:

```python
@dataclass
class Score:
    value: int = 0
```

Register it with the scene:

```python
def resources(self, ctx):
    return (
        Score(),
    )
```

Read it:

```python
score = ctx.world.get_resource(Score)
```

Resources are ideal for scene-wide state.

If many entities each need a value, that value is probably a component instead.

---

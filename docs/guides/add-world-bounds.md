# Add World Bounds

Define the play area:

```python
def bounds(self, ctx):
    return Bounds(
        left=40,
        right=600,
        top=40,
        bottom=680,
    )
```

Entities with bounds constraints can then use the engine's built-in bounds behavior.

Optionally render the border:

```python
def bounds_border(self, ctx):
    return WorldBoundsBorder(...)
```

The logical playfield can differ from the actual window.

---

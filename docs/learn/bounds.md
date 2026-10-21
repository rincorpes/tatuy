# Bounds

Scenes can define a logical world area.

```python
def bounds(self, ctx):
    return Bounds(...)
```

Tatuy then installs world-bounds resources.

Entities can use bounds constraints with behaviors such as:

- clamp
- bounce
- wrap
- despawn

The logical playfield does not have to equal the physical window.

A scene may also define a `WorldBoundsBorder` to render selected boundary sides.

---

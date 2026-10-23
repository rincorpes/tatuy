# Use Trails

Trails are ECS feature state owned by `tatuy.features.fx`.

A trail records recent positions from an entity's `Transform` and submits fading circles during presentation.

## Add a trail

```python
from tatuy.features.fx import Trail
from tatuy.features.spatial import Transform

entity = world.create_entity()
world.add_component(entity, Transform(Vec2(320, 180)))
world.add_component(
    entity,
    Trail(
        duration=0.5,
        interval=1 / 60,
        radius=6.0,
        max_points=48,
    ),
)
```

`TrailSystem` updates history and `TrailRenderSystem` submits presentation work. When those systems are part of the scene's game systems, the trail stays independent from backend drawing.

## Capacity and aging

`duration` controls how long a point survives. `interval` controls sampling frequency. `max_points` places a hard cap on retained trail history.

Disabling a trail stops new samples but existing points continue aging until removed.

Example: `examples/fundamentals/015_trails/app.py`.

See also [Effects](../learn/effects.md).

---
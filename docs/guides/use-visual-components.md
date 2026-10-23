# Use Visual Components

Use visual components when presentation belongs to an entity and should follow its `Transform` automatically.

## Supported visual components

Import them from the public visual facade:

```python
from tatuy.features.spatial import Transform
from tatuy.features.visual import Circle, Polygon, Rect, Text
```

A renderable entity combines `Transform` with one visual component.

```python
entity = world.create_entity()
world.add_component(entity, Transform(Vec2(320, 180)))
world.add_component(entity, Rect(Size(80, 40), (220, 220, 220), z=2))
```

Tatuy's built-in `RenderSystem` activates automatically when matching entities exist. Normal game scenes do not need to install it manually.

## Visibility, layer, and z

Each visual component carries presentation metadata such as `visible`, `layer`, and `z`.

Use `visible=False` to suppress submission without removing the component. Use `layer` for broad render groups and `z` for ordering within that layer.

## Polygon coordinates

`Polygon.vertices` are relative to `Transform.position`. The render system converts them to world-space points when submitting the draw operation.

## When not to use an entity

For transient debug text, one-frame effects, or presentation that has no persistent game identity, submit directly to `ctx.render_queue` or use `ctx.canvas` instead.

Examples:

- `examples/fundamentals/008_visual_components/001_rect/app.py`
- `examples/fundamentals/008_visual_components/002_circle/app.py`
- `examples/fundamentals/008_visual_components/003_polygon/app.py`
- `examples/fundamentals/008_visual_components/004_text/app.py`

See also [Rendering](../learn/rendering.md).

---
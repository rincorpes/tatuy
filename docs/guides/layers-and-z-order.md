# Use Layers and z-order

Tatuy separates broad presentation groups from ordering inside a group.

## Layers

Render layers are semantic groups:

```text
world
lighting
effects
postfx
ui
debug
```

The engine defines their broad ordering. Use a layer to describe what kind of presentation work an operation represents.

## z-order

Use `z` to order operations inside the same layer.

```python
ctx.render_queue.rect(
    center=Vec2(320, 180),
    size=Size(120, 60),
    color=(80, 80, 90),
    layer="world",
    z=0,
)

ctx.render_queue.text(
    x=320,
    y=180,
    text="Foreground",
    layer="world",
    z=10,
)
```

Operations with the same layer and `z` keep deterministic insertion order, but game logic should not use that tie-breaker as an implicit dependency when a distinct `z` is clearer.

Visual components expose the same `layer`/`z` model, so ECS-driven rendering and direct queue rendering participate in one ordered stream.

Example: `examples/fundamentals/009_rendering/004_layers_and_z/app.py`.

---
# Rendering

Tatuy separates game state from backend drawing.

Renderable entities combine a `Transform` with a visual component such as:

- `Rect`
- `Circle`
- `Polygon`
- `Text`

The built-in `RenderSystem` translates those entities into render-queue work.

## Direct rendering

Scenes and systems can also submit work directly:

```python
ctx.render_queue.text(...)
```

or use the canvas abstraction.

This is useful for:

- debug output
- simple HUD text
- transient presentation
- visual information that does not need an ECS entity

## Pipeline

```text
game state
    ↓
RenderQueue
    ↓
compile
    ↓
render packet
    ↓
RenderPipeline
    ↓
backend
```

---

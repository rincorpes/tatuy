# Rendering

Tatuy keeps game presentation backend-agnostic. Game code describes what should be drawn; the render pipeline decides how the active backend executes it.

## Visual entities

Persistent entity presentation uses a `Transform` plus a visual component:

```python
from tatuy.features.spatial import Transform
from tatuy.features.visual import Circle, Polygon, Rect, Text
```

The built-in `RenderSystem` translates matching entities into semantic render operations. Normal game scenes do not install the renderer manually.

Visual components own presentation properties such as visibility, render layer, and `z` ordering. Polygon vertices are relative to the entity transform and are resolved to world-space presentation data by the visual feature.

## Direct presentation

Presentation that does not need persistent ECS identity can use:

```python
ctx.render_queue.text(...)
```

or:

```python
ctx.canvas.rect(...)
```

Use direct presentation for debug output, transient HUD information, procedural marks, and one-frame effects.

`Canvas` is a convenience abstraction over semantic queue operations. It does not draw through a backend immediately.

## Ordering

All normal presentation participates in one semantic stream.

Order is determined by:

1. layer
2. `z`
3. insertion sequence as the deterministic final tie-breaker

Use layers for broad groups such as world, effects, UI, and debug. Use `z` when operations inside the same layer have a meaningful ordering dependency.

## Visual rendering versus UI rendering

World visuals and UI are separate feature owners:

```text
features.visual.RenderSystem
        ↓
     RenderQueue
        ↑
ui.UiRenderSystem
```

UI may reuse `features.visual.Text`, but the visual feature has no UI knowledge. Runtime composition activates world and UI rendering independently.

## Render pipeline

```text
visual/UI/feature presentation
            ↓
       RenderQueue
            ↓
         compile
            ↓
 RenderPacket / FramePacket
            ↓
      RenderPipeline
            ↓
     executor/backend
```

The queue and packet contain semantic presentation data rather than Pygame draw calls.

## Python fallback

Typed draw operations are the normal path and are intended to remain compatible with future native execution.

Tatuy also has an explicit Python custom-render fallback. It exists for presentation that cannot be represented by typed operations and receives a narrow Python render context. It should not become the default representation for ordinary rendering.

## What is implementation detail?

Normal game code should not depend on:

- render compiler classes
- packet assembly internals
- executor implementation classes
- Pygame renderer objects
- future native command-buffer representation

Those parts may change while `RenderQueue`, `Canvas`, visual components, UI rendering, and ordering semantics remain stable.

## Native preservation contract

A native renderer must preserve:

- typed command meaning
- layer/z ordering
- camera/view transforms
- screen-overlay semantics
- world/UI ordering behavior
- the explicit distinction between typed operations and Python fallback

## Examples

- `examples/fundamentals/008_visual_components/`
- `examples/fundamentals/009_rendering/001_render_system/app.py`
- `examples/fundamentals/009_rendering/002_render_queue/app.py`
- `examples/fundamentals/009_rendering/003_canvas/app.py`
- `examples/fundamentals/009_rendering/004_layers_and_z/app.py`

Related guides:

- [Use visual components](../guides/use-visual-components.md)
- [Use the render queue directly](../guides/use-render-queue.md)
- [Layers and z-order](../guides/layers-and-z-order.md)

See [Render Pipeline Architecture](../architecture/render-pipeline.md) for the implementation boundary.

---
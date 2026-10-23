# Render Pipeline

Tatuy separates game-facing presentation intent from backend execution.

The render architecture has three distinct ownership layers:

```text
game/features/UI
      ↓
semantic render data
      ↓
render compilation/execution
      ↓
backend/platform renderer
```

## Producers

Presentation work may come from several sources:

- `tatuy.features.visual.RenderSystem` converts world visual components into semantic draw operations
- `tatuy.ui.UiRenderSystem` converts resolved UI state into the same semantic stream
- feature presentation systems such as bounds borders and trails submit feature-owned render work
- scenes and game systems may submit directly through `RenderQueue` or `Canvas`

The visual feature and UI are intentionally separate. World rendering must not know about UI state, and UI must not be hidden inside the visual feature.

## RenderQueue

`RenderQueue` stores ordered render operations for one presentation pass.

Normal operations are typed semantic data:

```text
DrawOperation
    kind
    layer
    z
    seq
    payload: DrawCommand
```

Examples include rectangle, circle, polygon, line, text, and texture commands.

The queue does not hold a backend object and does not draw immediately.

## Ordering contract

Render order is determined by:

1. semantic layer
2. `z` within the layer
3. insertion sequence as the deterministic final tie-breaker

Layers provide broad grouping such as world, effects, UI, and debug. `z` expresses ordering dependencies within a layer.

This ordering is part of the observable rendering contract and must be preserved by future native implementations.

## Compilation

During scene presentation, Tatuy collects queue work and compiles it into prepared render packets.

Compilation may snapshot semantic values so the executor does not depend on mutable game state. Camera/view transforms and screen overlays are attached as presentation data.

Conceptually:

```text
Scene presentation
    ↓
RenderQueue
    ↓
compile
    ↓
RenderPacket / FramePacket
    ↓
RenderPipeline
```

## Python fallback

Tatuy also supports an explicit Python-only escape hatch:

```text
PythonRenderOperation
    payload: CustomCommand
```

A fallback callback receives a narrow `PythonRenderContext`, not the full backend object.

Fallback operations remain in the same ordered stream as typed operations, so layer/z/sequence behavior is preserved.

The important rule is:

> Python fallback is an explicit compatibility escape hatch, not the representation for normal rendering.

A future native executor may:

- execute typed operations natively
- route fallback operations back through Python
- reject fallback in a runtime that does not support Python callbacks

It must not require typed draw commands to carry Python backend objects merely because fallback exists.

## Backend execution

The executor translates prepared semantic work through backend rendering capabilities.

The current Pygame implementation is only one executor/backend path. Game code must not depend on Pygame draw calls or executor implementation classes.

```text
semantic operations
      ↓
executor boundary
      ↓
Pygame today
native/SDL/WebAssembly later
```

## Native replacement contract

A native render path must preserve:

- typed command meaning
- layer/z/sequence ordering
- camera/view application
- screen-overlay semantics
- visible/hidden behavior already resolved by producers
- the distinction between typed operations and Python fallback
- game-facing `RenderQueue`, `Canvas`, and visual/UI authoring behavior

Implementation details may change completely. The observable presentation model may not.

## Related documentation

- [Package ownership](package-ownership.md)
- [Game authoring contract](game-authoring-contract.md)
- [Rendering](../learn/rendering.md)
- [Use the render queue directly](../guides/use-render-queue.md)
- [Layers and z-order](../guides/layers-and-z-order.md)

---
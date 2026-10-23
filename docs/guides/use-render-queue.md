# Use the Render Queue Directly

Use `ctx.render_queue` when presentation does not need to live as ECS state.

Typical uses include debug markers, transient HUD elements, procedural presentation, and one-frame effects.

## Submit semantic draw work

```python
ctx.render_queue.circle(
    center=Vec2(320, 180),
    radius=24,
    color=(255, 220, 120),
    layer="effects",
    z=10,
)
```

The queue stores semantic render operations. It does not perform backend drawing immediately.

The engine later compiles the queue and executes the resulting operations through the active render executor/backend.

## Prefer typed operations

Normal rendering should use typed operations such as `rect`, `circle`, `line`, `poly`, `text`, and `texture`.

These operations are backend-agnostic and are the path intended to remain compatible with future native render execution.

Python custom rendering is an explicit fallback for cases that cannot be represented by typed operations. Do not use it as the default rendering model.

## Queue ordering

Every operation has:

- a render layer
- `z` within that layer
- insertion sequence as the final deterministic tie-breaker

Do not depend on insertion sequence when an explicit `z` expresses the real dependency more clearly.

Example: `examples/fundamentals/009_rendering/002_render_queue/app.py`.

See also [Render Pipeline](../architecture/render-pipeline.md) and [Layers and z-order](layers-and-z-order.md).

---
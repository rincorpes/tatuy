# Render Pipeline

Tatuy separates simulation state from backend rendering.

## Scene presentation

Each visible scene receives a fresh presentation queue.

```text
scene.on_present()
+
PRESENTATION systems
       ↓
RenderQueue
```

## Compilation

The queue is compiled into render data.

Camera and screen-effect snapshots are attached.

The result becomes a frame packet associated with the scene.

## Backend rendering

The engine's render pipeline translates compiled work through backend rendering capabilities.

This keeps:

```text
game presentation intent
```

separate from:

```text
Pygame drawing calls
```

and leaves room for future renderer/backend changes.

---

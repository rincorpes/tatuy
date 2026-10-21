# Render Pipeline Internals

The render path begins with scene `RenderQueue`s.

Presentation commands are compiled before backend execution.

Each visible scene produces a packet containing:

```text
scene ID
overlay flag
compiled render packet
camera view snapshot
screen overlay snapshot
```

The engine renderer then processes those packets through the selected backend.

---

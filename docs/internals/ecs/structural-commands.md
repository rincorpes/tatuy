# Structural Commands

Current structural commands:

```text
AddComponent
RemoveComponent
```

They are enqueued into a `StructuralCommandBuffer`.

At commit time, the buffer processes only the commands that were pending when the commit began.

Commands queued during a commit remain pending for a later barrier.

This keeps each barrier bounded and predictable.

---

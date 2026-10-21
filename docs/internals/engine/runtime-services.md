# Runtime Services Internals

`RuntimeServices` groups engine-facing runtime services such as:

```text
SceneService
ViewportService
EventsService
WindowService
InputService
CaptureService
AudioService
```

They are created by `TatuyApp` during engine composition.

Services translate between backend capabilities and higher-level engine behavior.

---

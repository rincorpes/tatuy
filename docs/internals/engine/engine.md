# Engine Implementation

`Engine` coordinates runtime execution.

Current supporting objects include:

```text
FrameInputCollector
SceneUpdater
ScenePresenter
FrameRenderer
EngineCommandProcessor
```

This keeps frame responsibilities separated rather than placing the entire frame inside one giant method.

The engine owns runtime state and coordinates services rather than implementing platform behavior itself.

---

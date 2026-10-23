# Engine Implementation

`Engine` coordinates lifecycle and frame orchestration. Concrete frame work is delegated to focused collaborators rather than implemented in `engine.py`.

Current supporting objects include:

```text
EngineConfig
    engine configuration

FrameInputCollector
    event and input synchronization

CaptureInputProcessor
    capture/replay shortcut handling

SceneUpdater
    scene update execution

ScenePresenter
    scene presentation and packet compilation

QueuedCanvas
    queue-backed Canvas implementation

FrameRenderer
    viewport, rendering, capture, and presentation coordination through a FrameRenderDriver contract

RenderExecutor
    replaceable execution boundary for prepared typed draw operations

EngineCommandProcessor
    queued engine commands
```

Primary ownership:

```text
engine.py
    lifecycle and frame orchestration

config.py
    EngineConfig

frame_input.py
    FrameInputCollector

capture_input.py
    CaptureInputProcessor

scene_update.py
    SceneUpdater

scene_presentation.py
    ScenePresenter

render/contracts.py
    FrameRenderDriver

render/renderer.py
    FrameRenderer

graphics/canvas.py
    Canvas and QueuedCanvas

graphics/render/packets.py
    RenderPacket and FramePacket

graphics/render/executor.py
    RenderExecutor and PythonRenderExecutor
```

The engine owns runtime state and coordinates services rather than implementing platform, scene execution, input synchronization, or rendering details itself.

---

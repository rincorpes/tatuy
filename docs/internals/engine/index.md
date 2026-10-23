# Engine Internals

Primary source:

```text
src/tatuy/engine/
```

Important areas:

```text
engine.py
    lifecycle and frame orchestration

config.py
    engine configuration

frame_input.py
    frame event/input coordination

capture_input.py
    capture and replay shortcut integration

scene_update.py
    scene update execution

scene_presentation.py
    scene presentation and packet compilation

scene.py
    scene stack/service

system.py
    generic scheduling and structural-commit contracts

pipelines.py
    generic pipeline factories

render/
    render compilation, driver contracts, pass selection, and FrameRenderer coordination

runtime/
    runtime composition/services and execution loop
    bootstrap.py assembles default scene-system dependencies
    builtins.py owns Tatuy's default feature registrations

command_processor.py
    engine commands
```

`QueuedCanvas` is owned by `src/tatuy/graphics/canvas.py` alongside the `Canvas` contract. Prepared `RenderPacket`/`FramePacket` data lives under `src/tatuy/graphics/render/packets.py`, while `src/tatuy/graphics/render/executor.py` defines the replaceable typed-command execution boundary.

---

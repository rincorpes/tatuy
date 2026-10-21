# Frame Lifecycle

The default loop repeatedly advances the engine.

Conceptually:

```text
PythonLoop
   ↓
Engine.start()
   ↓
Engine.step(...)
   ↓
Engine.step(...)
   ↓
...
   ↓
Engine.stop()
```

## Update

For active scenes, the engine:

```text
collect events/input
       ↓
select input scene
       ↓
update camera/screen effects
       ↓
update Intent
       ↓
scene.on_tick()
       ↓
system_pipeline.update()
```

The system pipeline itself contains the update phases and structural commits.

## Presentation

For visible scenes:

```text
create presentation RenderQueue
       ↓
scene.on_present()
       ↓
system_pipeline.present()
       ↓
compile queue
       ↓
attach camera/screen effect snapshots
       ↓
FramePacket
```

Packets are then passed to rendering.

## Timing

`dt` is elapsed seconds.

It is not the target frame duration.

`frame_index` is the loop iteration index.

The target FPS controls pacing rather than replacing measured elapsed time.

---

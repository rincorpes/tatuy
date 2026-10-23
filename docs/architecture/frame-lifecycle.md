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
compile queue into typed draw operations
       ↓
attach camera/screen effect snapshots
       ↓
RenderPacket
       ↓
FramePacket
```

`RenderPacket` and `FramePacket` are graphics-owned prepared frame data. Render passes select ordered operation batches, and a replaceable `RenderExecutor` consumes those batches. Custom Python callbacks use an explicit fallback path rather than the primary rendering representation.

Frame rendering is split into content execution and presentation. Capture runs after frame content has been rendered and before the frame is presented.

## Timing

`dt` is elapsed seconds.

It is not the target frame duration.

`frame_index` is the loop iteration index.

The target FPS controls pacing rather than replacing measured elapsed time.

## Host ownership

`Engine` does not own the outer scheduling loop. The host selects how the same lifecycle is driven:

```text
PythonLoop (default desktop)
    Engine.start()
    Engine.step(...)
    sleep/pacing
    Engine.stop()

AsyncioLoop (opt-in cooperative/browser host)
    Engine.start()
    Engine.step(...)
    await asyncio.sleep(0)
    Engine.stop()
```

`TatuyApp.run()` continues to use the synchronous `PythonLoop`. `TatuyApp.run_async()` is an explicit alternate host path; Tatuy does not switch execution models by detecting a browser implicitly.

---
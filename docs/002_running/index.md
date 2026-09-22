# Running Tatuy

The [backend](../001_backend/index.md) knows how to open a window, collect events, and draw. Something still has to decide **when** those things happen. That is the job of the engine and its loop.

```text
TatuyApp builds a Runtime
    Runtime holds an Engine and a PythonLoop
        PythonLoop calls Engine.start(), Engine.step(), and Engine.stop()
            Engine coordinates services, scenes, and rendering
                Backend performs platform operations
```

You can assemble these pieces yourself or let `TatuyApp` do it. For a game, `TatuyApp` is the shortest path. The lower-level forms are useful when you want to understand or replace part of the setup.

| Piece | Responsibility |
| --- | --- |
| `Engine` | Owns the running state and coordinates one frame through `step(dt, frame_index)`. |
| `PythonLoop` | Measures time, calls `step`, and requests a target frame rate. |
| `Runtime` | Holds an engine and a loop and starts them together. |
| `TatuyApp` | Builds the backend, engine, services, and loop from configuration. |

## Starting and stopping

The engine's lifecycle is:

```text
engine.start()  →  engine.step(...) each frame  →  engine.stop()
```

`start()` initializes the backend, opens the window, initializes the viewport, and enters the configured starting scene. The default scene ID is `main`. Register or import that scene before starting the engine; otherwise the window can open with no active scene.

`stop()` closes capture work and releases backend resources. The loop calls it in a `finally` block so normal exits and exceptions both clean up. If you write your own loop, give it the same protection.

Do not call `backend.init()` or `backend.window.open()` before `engine.start()`. The engine does both. The [backend lifecycle](../001_backend/lifecycle.md) describes the lower-level path for programs that use the backend directly.

## One frame

Each call to `engine.step(dt, frame_index)` polls events, updates window and input state, handles capture and replay, updates scenes, processes engine commands, builds drawing commands, renders, and presents the frame. A quit event can set `engine.running` to `False` during that call.

`dt` is elapsed time **in seconds** since the previous frame. It is not a frame number or a target duration. For example, `0.016` is roughly 16 milliseconds. A scene can multiply a speed in pixels per second by `ctx.dt` to get movement for this frame.

`frame_index` counts loop iterations. Start at zero and increment once after each call to `step`.

The target FPS is a pacing request, not the value to pass as `dt`. At 60 FPS, the target duration is `1 / 60` seconds; actual frame duration can vary with rendering, scheduling, and sleep accuracy. A long pause can also produce a large `dt`, so games that need a fixed simulation step need an accumulator or another timing policy above the basic loop.

## Which entry point should I use?

Start with `TatuyApp` when writing a game:

```python
from tatuy.app import TatuyApp

TatuyApp().run()
```

Use `Runtime` if you are constructing the backend, engine, and loop yourself. Use `PythonLoop` directly if you do not need the extra container. Write a manual loop only when you need to control timing or embedding yourself; it has to handle `dt`, frame pacing, and shutdown.

The [running examples](./examples.md) show each entry point in that order. Once you have a loop, [scenes](../003_scenes/index.md) give it something to run.

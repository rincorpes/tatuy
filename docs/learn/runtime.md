# Learn Runtime

A normal Tatuy game starts with `TatuyApp`.

Underneath that convenience layer are several smaller pieces:

```text
TatuyApp
    ├── run()       → Runtime + PythonLoop
    └── run_async() → AsyncRuntime + AsyncioLoop
                     ↓
                   Engine
```

The synchronous desktop path remains the default. The async path is explicit and intended for cooperative hosts such as browser runtimes; Tatuy does not detect the browser implicitly.

## TatuyApp

`TatuyApp` is the normal game entry point.

It:

- reads application configuration
- builds registered settings
- configures the profiler
- creates the backend
- creates runtime services
- creates the engine
- creates the loop
- builds a `Runtime`

## Runtime

`Runtime` bundles an engine and a synchronous loop. `AsyncRuntime` provides the equivalent composition for an asynchronous host.

Neither is a second hidden execution system; both delegate lifecycle ownership to the configured loop.

## PythonLoop

`PythonLoop` repeatedly advances the engine and controls desktop frame pacing with the configured target FPS.

Game code usually does not need to manage this directly.

## AsyncioLoop

`AsyncioLoop` preserves the same `Engine.start()` / `Engine.step()` / `Engine.stop()` lifecycle while yielding to the host with `await asyncio.sleep(0)` after each successful frame.

Use it explicitly through:

```python
await TatuyApp(
    {
        "app": {"async_loop": "asyncio"},
        "capabilities": {"capture": False},
    }
).run_async()
```

`run()` still uses `PythonLoop`; adding async/browser hosting does not change existing desktop execution.

## Engine

The engine coordinates:

- events
- input
- scenes
- system execution
- commands
- rendering
- capture
- backend presentation

## Which entry point?

| Need | Start with |
| --- | --- |
| Normal desktop game | `TatuyApp.run()` |
| Cooperative/browser-style host | `TatuyApp.run_async()` |
| Manually supply engine + sync loop | `Runtime` |
| Manually supply engine + async loop | `AsyncRuntime` |
| Use Tatuy's desktop loop with custom composition | `PythonLoop` |
| Use Tatuy's cooperative loop with custom composition | `AsyncioLoop` |
| Control stepping yourself | `Engine` |

Normal game code should usually choose `TatuyApp`.

For exact frame behavior, see [Frame lifecycle](../architecture/frame-lifecycle.md).

---

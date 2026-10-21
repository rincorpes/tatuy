# Learn Runtime

A normal Tatuy game starts with `TatuyApp`.

Underneath that convenience layer are several smaller pieces:

```text
TatuyApp
    ↓
Runtime
├── Engine
└── PythonLoop
```

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

`Runtime` bundles an engine and a loop.

It is composition, not a second hidden execution system.

## PythonLoop

The loop repeatedly advances the engine and controls frame pacing.

Game code usually does not need to manage this directly.

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
| Normal game | `TatuyApp` |
| Manually supply engine + loop | `Runtime` |
| Use Tatuy's loop with custom composition | `PythonLoop` |
| Control stepping yourself | `Engine` |

Normal game code should usually choose `TatuyApp`.

For exact frame behavior, see [Frame lifecycle](../architecture/frame-lifecycle.md).

---

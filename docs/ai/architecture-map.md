# Architecture Map

Canonical package ownership and dependency-direction rules are defined in `docs/architecture/package-ownership.md`. Use that document when deciding where a new type belongs or whether a cross-package import is allowed.

## Application

```text
src/tatuy/app.py
```

## Engine

```text
src/tatuy/engine/
```

Important:

```text
engine.py
config.py
frame_input.py
capture_input.py
scene_update.py
scene_presentation.py
scene.py
system.py
pipelines.py
render/
    contracts.py
    renderer.py
    compiler.py
    pipeline/
runtime/
    bootstrap.py
    builtins.py
```

`system.py` and `pipelines.py` define generic scheduling contracts. Default feature registrations and lifecycle-aware structural commitment are assembled under `runtime/` so the engine core does not import concrete feature implementations.

## Scenes

```text
src/tatuy/scenes/
```

## ECS

```text
src/tatuy/ecs/
```

## Entity construction

```text
src/tatuy/ecs/entity/blueprint.py
src/tatuy/ecs/entity/factory.py
src/tatuy/features/visual/blueprints.py
src/tatuy/features/collision/blueprints.py
```

The ECS-owned blueprint/factory layer is feature-agnostic. Built-in visual and collision construction policy lives with the owning features.

## Structural commands

```text
src/tatuy/ecs/structural.py
```

## Features

```text
src/tatuy/features/
├── bounds/
├── collision/
├── fx/
├── lifecycle/
├── movement/
├── spatial/
└── visual/
```

Performance-sensitive feature work may be delegated to replaceable kernels. See `docs/architecture/kernels.md`; current reference kernels live under movement, bounds, spatial, collision, lifecycle, and FX features.

## Graphics

```text
src/tatuy/graphics/
```

`graphics/canvas.py` owns the `Canvas` contract and the queue-backed `QueuedCanvas` implementation used by scene execution.

`graphics/render/packets.py` owns prepared `RenderPacket` and `FramePacket` data. `graphics/render/executor.py` owns the replaceable command-execution boundary. Compiled packets contain typed draw operations; custom Python callbacks remain an explicit fallback path rather than the primary rendering representation.

## Backend

```text
src/tatuy/backend/
```

## Input

```text
src/tatuy/input/
```

## Audio

```text
src/tatuy/audio/
```

## Capture

```text
src/tatuy/capture/
```

## UI

```text
src/tatuy/ui/
```

## Profiler

```text
src/tatuy/tooling/profiler/
src/tatuy_profiler/
```

## MCP

```text
src/tatuy_mcp/
```

## Examples

```text
examples/fundamentals/
examples/experiments/
examples/games/
```

---

# Architecture at a Glance

## Top level

```text
TatuyApp
   │
   ▼
Runtime
├── PythonLoop
└── Engine
     ├── Runtime services
     ├── SceneService
     ├── System pipeline
     ├── Render pipeline
     └── Backend
```

`TatuyApp` is the normal entry point.

It constructs configuration, services, the backend, engine, and loop.

## Scene

```text
Scene
├── World
│   ├── Entities
│   ├── Components
│   └── Resources
├── Intent
├── Spawn definitions
├── Initial entities
├── Game systems
└── Presentation hooks
```

A scene represents one active part of the game.

## ECS

```text
Entity
    identity

Component
    per-entity data

Resource
    scene-wide data

System
    behavior
```

Systems query component combinations and operate on the matching entities.

## Input

```text
keyboard / mouse
       ↓
   InputFrame
       ↓
     Intent
       ↓
 Game systems
```

Raw device input is translated into game meaning.

## Systems

A `BaseSystem` runs in one phase.

A `GameSystem` can participate in several:

```text
on_control
on_pre_simulation
on_simulation
on_post_simulation
on_presentation
```

## Pipeline

```text
CONTROL
    ↓
PRE_SIMULATION
    ↓
PRE_SIM_COMMIT
    ↓
SIMULATION
    ↓
POST_SIMULATION
    ↓
POST_SIM_COMMIT

then

PRESENTATION
```

Commit phases synchronize structural ECS changes.

## Built-ins

Tatuy automatically supplies reusable systems such as:

- movement
- velocity integration
- bounds
- attachments
- collisions
- lifetime processing
- rendering

They use activation predicates so irrelevant built-ins do not perform their normal work.

## Rendering

```text
World
   ↓
RenderSystem / game presentation
   ↓
RenderQueue
   ↓
compiled render packet
   ↓
RenderPipeline
   ↓
Backend renderer
```

## Backend

```text
Backend
├── Events
├── Window
├── Input
├── Renderer
├── Audio
└── Capture
```

Pygame currently implements these capabilities.

## Profiling

Tatuy records hierarchical execution information across:

```text
frame
├── runtime
├── scene
├── pipeline
├── system
├── lifecycle
├── rendering
└── custom game spans
```

---

# Tatuy

**A Python-first 2D game engine built to stay understandable as it grows.**

Tatuy is an experimental 2D game engine built around scenes, an Entity Component System (ECS), explicit system phases, reusable gameplay features, and a replaceable backend boundary.

Games stay in Python. Engine behavior remains visible. Performance-sensitive infrastructure can move elsewhere when there is an actual reason to move it.

Today, Tatuy runs on Pygame.

Tomorrow? Maybe SDL2 and native code.

The game should not have to care.

```text
Game
 │
 ▼
Scenes + Game Systems
 │
 ▼
ECS + Engine Features
 │
 ▼
System / Render Pipelines
 │
 ▼
Backend Boundary
 │
 ▼
Pygame
```

## Why Tatuy?

Tatuy started from a simple idea:

> Write games in Python, then move performance-sensitive infrastructure somewhere faster when it actually becomes a problem.

Tatuy tries to make questions about execution answerable:

- What runs before collision detection?
- When is a spawned entity actually created?
- Which systems ran this frame?
- Which built-ins activated automatically?
- Why did this frame take 20 ms?
- Could the renderer eventually move to native code without rewriting the game?

The engine follows a few principles:

- Gameplay should remain approachable.
- Frame execution should be explicit.
- Reusable mechanics belong in the engine.
- Game rules belong in the game.
- Structural ECS changes happen at controlled synchronization points.
- Backend-specific behavior stays behind a backend boundary.
- Optimization follows measurement.

Sometimes abstraction is just procrastination wearing glasses.

Tatuy tries to keep the abstractions that have an actual job.

## Status

Current version:

```text
0.1.0
```

Tatuy is alpha software.

The architecture is still evolving as increasingly complex games and experiments expose weaknesses in the engine.

Current requirements:

- Python 3.10–3.12
- `onomasticon` for the core runtime registries
- Pygame only for the current reference desktop backend
- Pillow only for image capture
- FFmpeg only for MP4 capture

## Get started

For repository development:

```bash
poetry install -E dev
poetry run python manage.py run example scenes.on_present
```

For a packaged desktop game install:

```bash
pip install "tatuy[pygame]"
```

For browser packaging/build tooling:

```bash
pip install "tatuy[web]"
```

The minimal `tatuy` install intentionally excludes the Pygame backend, browser packaging, capture, CLI, and MCP dependencies. See [`docs/internals/runtime-dependencies.md`](docs/internals/runtime-dependencies.md) for the extras model.

A desktop environment is required for interactive Pygame examples.

## Core architecture

```text
TatuyApp
   │
   ▼
Runtime
   │
   ▼
Engine
   │
   ▼
Scene stack
   │
   ▼
Scene
├── World
│   ├── Entities
│   ├── Components
│   └── Resources
├── Intent
├── Game Systems
└── System Pipeline
    ├── CONTROL
    ├── PRE_SIMULATION
    ├── PRE_SIM_COMMIT
    ├── SIMULATION
    ├── POST_SIMULATION
    ├── POST_SIM_COMMIT
    └── PRESENTATION
```

Tatuy currently includes reusable behavior for:

- transforms and attachments
- movement
- bounds
- collisions
- spawning and despawning
- lifetimes and respawning
- shapes, text, and polygons
- particles and effects
- UI
- audio
- screenshots
- deterministic input replay
- video capture
- profiling

## Documentation

### Understand Tatuy

- [`docs/overview/why-tatuy.md`](docs/overview/why-tatuy.md)
- [`docs/overview/architecture-at-a-glance.md`](docs/overview/architecture-at-a-glance.md)
- [`docs/overview/features.md`](docs/overview/features.md)

### Build a game

- [`docs/getting-started/`](docs/getting-started/)
- [`docs/learn/`](docs/learn/)
- [`docs/guides/`](docs/guides/)

### Look something up

- [`docs/reference/`](docs/reference/)

### Understand the engine

- [`docs/architecture/`](docs/architecture/)
- [`docs/internals/`](docs/internals/)

### Use AI to work on Tatuy

- [`AGENTS.md`](AGENTS.md)
- [`docs/ai/`](docs/ai/)

## Examples

```text
examples/
├── fundamentals/   Focused concepts
├── experiments/    Architecture and performance exploration
└── games/          Larger integrations
```

See [`docs/examples/`](docs/examples/).

## Repository

```text
src/
├── tatuy/             Engine and game-building APIs
├── tatuy_cli/         Repository tooling
├── tatuy_mcp/         AI development access
└── tatuy_profiler/    Profile viewer
```

## Direction

Tatuy is currently focused on:

- robust 2D gameplay
- explicit execution
- reusable engine features
- real game experiments
- profiling and debugging
- Python-first game code
- backend independence
- discovering which infrastructure may eventually deserve native implementation

If an architecture only works with one rectangle on screen, it probably is not finished yet.

## License

MIT.

---

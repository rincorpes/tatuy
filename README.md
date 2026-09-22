# Tatuy

Build small 2D games in Python with code you can follow.

Tatuy is a Python 2D game engine built around scenes, an Entity Component System (ECS), and separate gameplay and rendering stages. It provides reusable systems for movement, collisions, entity lifecycles, and UI, with Pygame as its current backend.

The repository includes fundamental examples, Pong, and Breakout, plus built-in screenshot, replay, and video recording tools.

## Status

Tatuy is in early development, currently version 0.0.1. APIs and examples may change as the engine evolves.

## Get started

The project has support for Python 3.10–3.12 and uses Poetry to manage dependencies.

From the repository root:

```bash
poetry install
poetry run python manage.py run game pong
```

A desktop environment is required to display the game window. FFmpeg is required for MP4 video encoding.

## How Tatuy works

A Tatuy game is organized around a few building blocks:

| Building block | Responsibility |
| --- | --- |
| Application | Builds the backend, engine, services, and loop |
| Scene | Owns a game screen or overlay and its lifecycle |
| World | Stores entities, components, and shared scene resources |
| Component | Holds data such as position, velocity, or appearance |
| Intent | Translates an input frame into game-specific actions |
| System | Implements behavior by querying and updating components |
| Command | Requests an engine action, such as changing scenes |
| Render queue | Collects drawing operations for presentation |

Systems participate in control, simulation, or presentation. A scene's system list makes execution order explicit.

For example, a movement system can operate on every entity with a position and velocity:

```python
from tatuy.ecs.component import Transform, Velocity
from tatuy.ecs.system import BaseSystem


class MoveSystem(BaseSystem):
    def step(self, ctx):
        for _, transform, velocity in ctx.world.query(
            Transform, Velocity
        ):
            transform.position.x += velocity.value.x * ctx.dt
            transform.position.y += velocity.value.y * ctx.dt
```

Tatuy already provides this behavior through `VelocityIntegrationSystem`.

Scenes can also draw directly during `on_present`, using their canvas or render queue.

## Included capabilities

- Scene changes and stacked overlays, with policies for visibility, input, and updates.
- Component queries, shared resources, and entity blueprints.
- Velocity integration and movement controls.
- Box and circle collision detection, sensors, collision response, and custom velocity rules.
- Bounds behaviors: clamp, bounce, wrap, and despawn.
- Queued spawning, delayed respawning, and entity lifetimes.
- UI panels and buttons with hierarchy, anchors, pointer handling, and appearance states.
- Layered drawing of shapes, text, and textures.
- Sound loading and playback.
- PNG screenshots, input replay, and silent MP4 recording.

## Capture and replay

Screenshot and video hotkeys are enabled by default. Replay hotkeys require replay to be enabled in the game settings; the Pong example enables them.

| Key | Action |
| --- | --- |
| F2 | Save a screenshot |
| F3 | Start recording a replay |
| F4 | Stop recording a replay |
| F5 | Play the configured replay |
| F6 | Stop playback and return to the starting scene |
| F7 | Start video recording |
| F8 | Stop video recording and begin encoding |

Capture output defaults to:

```text
.tatuy/
├── screenshots/
├── replays/
└── recordings/
```

Replay files store inputs and simulation timing, rather than video. Their headers also store the starting scene, seed, dimensions, and game-specific options.

Starting a replay recording recreates its initial scene. Repeatable playback depends on game code using consistent initial state and the recorded seed. Playback requires matching recorded dimensions.

Video recording captures rendered frames and encodes them with FFmpeg. Game audio is not included.

## Explore the examples

Fundamental examples cover backend initialization, windows, events, input, the runtime loop, scenes, ECS, movement, bounds, spawning, and collisions.

Run an example using its logical folder names, without numeric prefixes:

```bash
poetry run python manage.py run example scenes.render
```

Use dots to address nested examples:

```bash
poetry run python manage.py run example ecs.components.query
```

The numbered folders preserve the examples' organization while the CLI accepts readable names.

## Repository layout

```text
src/
├── tatuy/             Engine and game-building APIs
│   ├── backend/       Backend protocols and Pygame implementation
│   ├── ecs/           Worlds, components, blueprints, and systems
│   ├── engine/        Frame loop, scene stack, and rendering pipeline
│   ├── scenes/        Scene lifecycle, intents, and contexts
│   ├── graphics/      Drawing commands and viewport utilities
│   ├── geometry/      Shapes, bounds, collision math, and grids
│   ├── physics/       Collider access and collision rules
│   ├── input/         Keyboard and pointer input snapshots
│   ├── ui/            Layout, interaction, and rendering
│   ├── audio/         Runtime audio service
│   └── capture/       Screenshots, replay, and video recording
└── tatuy_cli/         Commands for running repository examples

examples/
├── fundamentals/      Focused examples of individual concepts
└── games/             Pong and Breakout
```

## Current scope

Pygame is the only implemented backend. Entity-to-entity collision detection currently supports boxes and circles.

Rendering includes layers for lighting and effects, but advanced lighting, post-processing, and viewport scaling are still developing.

Start with the reference games to see how the current pieces fit together.

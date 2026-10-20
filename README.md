# Tatuy

Build 2D games in Python with an engine whose architecture you can follow.

Tatuy is an experimental Python 2D game engine built around scenes, an Entity Component System (ECS), explicit system phases, and a separation between simulation and presentation.

It provides reusable engine features for movement, collisions, bounds, entity lifecycles, rendering, UI, audio, capture, replay, and profiling, with Pygame as the current backend.

Tatuy is being developed alongside real game prototypes, so the engine favors practical, reusable systems over hiding game behavior behind a large framework.

## Status

Tatuy is in early development and is currently version `0.1.0`.

APIs are still evolving as the engine is exercised by increasingly complex games and experiments. Documentation and older examples may occasionally lag behind the current implementation.

Current requirements:

- Python 3.10–3.12
- Poetry
- Pygame backend
- FFmpeg for MP4 capture

## Get started

From the repository root:

```bash
poetry install
poetry run python manage.py run example scenes.on_present
```

A desktop environment is required for interactive examples.

Examples can be addressed using their logical names rather than their numeric directory prefixes.

For example:

```bash
poetry run python manage.py run example scenes.on_present
poetry run python manage.py run example backend.renderer.shapes
```

## How Tatuy is organized

A Tatuy game is built from a small set of concepts:

| Building block | Responsibility |
| --- | --- |
| `TatuyApp` | Builds configuration, backend, engine, services, and loop |
| Scene | Defines one game screen, level, overlay, or game state |
| World | Stores entities, components, and scene resources |
| Entity | An ID representing a game object |
| Component | Data attached to an entity |
| Resource | Scene-wide shared state |
| Intent | Converts input into game-specific actions |
| System | Implements behavior over entities and resources |
| Spawn definition | Describes how an entity type is created |
| Structural command | Defers changes to ECS structure until a safe commit point |
| Render queue | Collects presentation commands before rendering |
| Command | Requests an engine-level action such as changing scenes |

The general flow is:

```text
Application
    │
    ▼
 Runtime / Engine
    │
    ▼
 Scene
    │
    ├── World
    │   ├── Entities
    │   ├── Components
    │   └── Resources
    │
    ├── Intent
    │
    ├── Systems
    │
    └── Render Queue
```

## Scenes

A scene describes the state needed to run part of a game.

A scene defines its world, intent, tick context, resources, entity population, and game systems.

A current scene usually looks conceptually like this:

```python
from tatuy.ecs.world import World
from tatuy.scenes.context import Intent, SceneTickContext
from tatuy.scenes.registry import SceneRegistry
from tatuy.scenes.scene import EntitySpawn, Scene


class GameWorld(World):
    pass


class GameIntent(Intent):
    pass


class GameTickContext(SceneTickContext[GameWorld, GameIntent]):
    pass


@SceneRegistry.implementation("main")
class MainScene(Scene[GameWorld, GameIntent, GameTickContext]):
    world_type = GameWorld
    intent_type = GameIntent
    tick_context_type = GameTickContext

    def resources(self, ctx):
        return ()

    def spawn_definitions(self, ctx):
        return {}

    def entities(self, ctx):
        return ()

    def game_systems(self, ctx):
        return ()

    def on_enter(self, ctx):
        pass
```

Scenes provide several extension points.

### `resources()`

Returns scene-level resources to insert into the world.

Resources are useful for state shared across many entities or systems:

```python
def resources(self, ctx):
    return (
        Score(),
        GameState(),
        CollisionFrame(),
    )
```

### `spawn_definitions()`

Declares reusable entity spawn definitions.

A `SpawnDefinition` associates a name with an entity factory entry and optionally supplies default arguments.

```python
def spawn_definitions(self, ctx):
    return {
        "enemy": SpawnDefinition("enemy"),
        "ball": SpawnDefinition("ball"),
    }
```

### `entities()`

Defines the scene's initial population.

```python
def entities(self, ctx):
    yield EntitySpawn("player")
    yield EntitySpawn("ball")
```

Initial entities are queued through Tatuy's lifecycle system rather than created directly as part of scene configuration.

### `game_systems()`

Returns game-specific behavior:

```python
def game_systems(self, ctx):
    return (
        PlayerSystem(),
        EnemySystem(),
        WaveSystem(),
    )
```

### `bounds()`

Scenes can define world bounds:

```python
def bounds(self, ctx):
    return Bounds(
        left=0,
        right=ctx.viewport.virtual_w,
        top=0,
        bottom=ctx.viewport.virtual_h,
    )
```

When bounds are supplied, Tatuy installs the corresponding world-bounds resources automatically.

## ECS

Tatuy's ECS separates game objects into entities, components, systems, and resources.

An entity itself is only an identifier.

Components contain state:

```python
Transform
Velocity
Movement
CollisionBody
CircleCollider
Rect
Circle
Polygon
Text
Lifetime
```

A system queries combinations of components:

```python
for entity, transform, velocity in ctx.world.query(
    Transform,
    Velocity,
):
    transform.position += velocity.value * ctx.dt
```

Tatuy's built-in velocity integration already provides this particular behavior, so games normally add `Transform` and `Velocity` and let the engine activate the required built-in system.

This is an important part of Tatuy's design: **games describe their state, while reusable engine behavior activates when that state requires it.**

## Features

Reusable gameplay functionality lives primarily under `tatuy.features`.

Current areas include:

- spatial transforms and attachments
- movement and velocity integration
- world bounds
- collision detection and response
- entity lifecycle
- visual components
- particles and other effects

Game-specific behavior should normally stay in the game. Engine features are intended for behavior that can be reused across different games.

## System pipeline

Tatuy systems run through an explicit phase pipeline.

The current phases are:

```text
CONTROL
PRE_SIMULATION
PRE_SIM_COMMIT
SIMULATION
POST_SIMULATION
POST_SIM_COMMIT
PRESENTATION
```

The two commit phases are structural barriers.

```text
CONTROL
    │
PRE_SIMULATION
    │
PRE_SIM_COMMIT
    │
    └── apply queued structural changes
    │
SIMULATION
    │
POST_SIMULATION
    │
POST_SIM_COMMIT
    │
    └── apply queued structural changes
    │
PRESENTATION
```

Structural changes include operations such as queued spawning, despawning, and deferred ECS modifications.

This lets systems iterate safely without other systems unexpectedly changing the structure of the world in the middle of the same phase.

### `BaseSystem`

A `BaseSystem` participates in one phase:

```python
from tatuy.ecs.system import BaseSystem, SystemPhase


class EnemyMovementSystem(BaseSystem):
    phase = SystemPhase.SIMULATION
    order = 100

    def step(self, ctx):
        ...
```

### `GameSystem`

A `GameSystem` can participate in several phases while keeping behavior that belongs to one gameplay concept together.

```python
from tatuy.ecs.system import GameSystem, SystemPhase


class EnemySystem(GameSystem):
    phase_orders = {
        SystemPhase.SIMULATION: 30,
        SystemPhase.POST_SIMULATION: 200,
        SystemPhase.PRESENTATION: 20,
    }

    def on_simulation(self, ctx):
        ...

    def on_post_simulation(self, ctx):
        ...

    def on_presentation(self, ctx):
        ...
```

Supported game-system hooks are:

```python
on_control()
on_pre_simulation()
on_simulation()
on_post_simulation()
on_presentation()
```

Only hooks overridden by the game system are scheduled.

This makes `GameSystem` useful when one gameplay concept needs to react at several points in a frame without being split into several unrelated classes.

## Built-in systems

Tatuy installs a catalog of reusable systems for every scene.

These systems are automatically activated when the required components or resources are present.

Current built-ins include behavior for:

### Control

- movement controls

### Pre-simulation

- delayed spawning
- motion snapshots
- movement calculations

### Simulation

- velocity integration
- bounds constraints
- entity attachments
- collision detection
- collision response

### Post-simulation

- bounds direction synchronization
- collision direction synchronization
- entity lifetime processing

### Presentation

- entity rendering
- world-bounds rendering

Because activation is automatic, a scene generally does not need to manually instantiate common built-in systems.

For example, entities containing both:

```python
Transform
Velocity
```

cause velocity integration to become active automatically.

## Overriding built-ins

Games sometimes need different scheduling or custom behavior around an engine feature.

Scenes can replace or remove built-in registrations through `builtin_overrides()`.

For example:

```python
def builtin_overrides(self, ctx):
    return {
        "collision_detection": None,
    }
```

Returning `None` disables that built-in for the scene.

A built-in can also be replaced with a custom `SystemRegistration`:

```python
def builtin_overrides(self, ctx):
    return {
        "collision_response": SystemRegistration(
            CollisionResponseSystem(),
            phase=SystemPhase.POST_SIMULATION,
            order=500,
        ),
    }
```

This provides an escape hatch for advanced games without requiring changes to the engine's global scheduling rules.

## Movement

Tatuy includes components and systems for several levels of movement behavior.

At the lowest level:

```text
Transform + Velocity
        │
        ▼
VelocityIntegrationSystem
        │
        ▼
position changes
```

Higher-level movement can use:

```text
MovementControls
DesiredMovement
Movement
Velocity
Transform
```

to separate:

1. player or AI intent
2. desired movement
3. acceleration and speed rules
4. final velocity
5. spatial integration

This keeps control logic separate from movement physics.

## Bounds

World bounds are scene resources rather than hard-coded screen limits.

Entities can use bounds constraints with behaviors such as:

- clamp
- bounce
- wrap
- despawn

Scenes may also render selected world-boundary sides with `WorldBoundsBorder`.

This allows the logical playfield to differ from the physical window.

## Collision

Tatuy currently supports reusable collision components and response systems.

Collider types include:

- box
- circle
- polygon

Collision state is collected into a `CollisionFrame`, allowing game systems to inspect contacts after detection.

This makes it possible for game rules to respond to collision events without embedding gameplay decisions inside the collision detector itself.

For example:

```text
Collision detection
        │
        ▼
CollisionFrame
        │
        ├── game rules
        ├── scoring
        ├── damage
        ├── pickups
        └── effects
        │
        ▼
Collision response
```

Games that need more control over this ordering can override the built-in collision registrations.

## Entity lifecycle

Entity creation and destruction can be queued rather than performed immediately.

Tatuy's lifecycle support includes:

- spawn definitions
- queued spawning
- delayed spawning
- despawning
- lifetimes
- respawning

Scenes automatically receive:

```python
LifecycleQueue
SpawnRegistry
```

unless they already provide them.

The structural commit barriers then apply queued lifecycle changes at safe points in the frame.

This is particularly useful when systems need to spawn or remove entities while iterating over ECS queries.

## Rendering

Simulation and rendering are intentionally separated.

Renderable entities use spatial and visual components such as:

```python
Transform
Rect
Circle
Polygon
Text
```

The built-in render system converts them into presentation work automatically.

Scenes and game systems can also submit rendering directly through the render queue:

```python
ctx.render_queue.text(
    x=100,
    y=100,
    text="Hello Tatuy",
    color=(255, 255, 255),
    font_size=20,
)
```

This is useful for debug information, HUD elements, temporary effects, and rendering that does not justify creating an ECS entity.

Tatuy also includes camera and screen-effect infrastructure that can be shared by game systems.

## Input and intent

Tatuy separates raw input from game intent.

Instead of every system reading keyboard or pointer state directly, a scene defines an `Intent` that translates the current input frame into meaningful game actions.

Conceptually:

```text
Keyboard / Mouse / Gamepad
            │
            ▼
       InputFrame
            │
            ▼
          Intent
            │
            ▼
       Game Systems
```

This improves separation between device input and gameplay logic and also helps deterministic replay.

## Scene stack

Tatuy supports multiple scenes and stacked overlays.

Scene policies allow different combinations of:

- visibility
- updating
- input handling

This makes the scene system suitable for concepts such as:

- game screens
- pause menus
- overlays
- modal interfaces
- transitions

Engine commands are used to request scene changes instead of coupling game systems directly to the scene service.

## Capture and replay

Tatuy includes screenshot, replay, and video capture support.

Default hotkeys include:

| Key | Action |
| --- | --- |
| F2 | Save screenshot |
| F3 | Start replay recording |
| F4 | Stop replay recording |
| F5 | Play configured replay |
| F6 | Stop replay playback |
| F7 | Start video recording |
| F8 | Stop video recording and begin encoding |

Runtime output is stored under `.tatuy/`, including capture and profiling data.

A typical layout is:

```text
.tatuy/
├── screenshots/
├── replays/
├── recordings/
└── profiles/
```

Replay files record input and simulation information rather than rendered video.

Repeatable playback therefore depends on the game starting from deterministic state and using the recorded seed consistently.

Video recording captures rendered frames and uses FFmpeg for encoding. Game audio is currently not included in recorded video.

## Profiling

Tatuy includes an engine-aware profiler designed to expose where time is spent during a frame.

Profiling can be enabled in application configuration:

```python
TatuyApp(
    {
        "profiler": {
            "enabled": True,
        },
    }
)
```

When profiling is enabled, Tatuy records hierarchical spans for areas such as:

```text
frame
├── scene
├── system pipeline
│   ├── CONTROL
│   ├── PRE_SIMULATION
│   ├── structural commit
│   ├── SIMULATION
│   ├── POST_SIMULATION
│   └── structural commit
├── presentation
└── engine/runtime services
```

System spans include scheduling information such as phase and order.

The profiler can also record metrics and annotations from game code:

```python
from tatuy.tooling.profiler import profiler


with profiler.span("enemy.update", "game"):
    ...

profiler.metric("enemies", enemy_count)
```

When the application exits with profiling enabled, the latest profile is exported to:

```text
.tatuy/profiles/latest.json
```

and a report including slow frames is printed.

The repository also contains a lightweight profile viewer:

```bash
poetry run python -m tatuy_profiler .tatuy/profiles/latest.json
```

It opens the profiler UI locally in the browser.

## Configuration

A Tatuy application is configured through a dictionary passed to `TatuyApp`.

For example:

```python
app = TatuyApp(
    {
        "engine": {
            "fps": 120,
            "debug_overlay": True,
        },
        "backend": {
            "window": {
                "width": 1280,
                "height": 720,
            },
            "renderer": {
                "background_color": (15, 18, 32),
            },
        },
        "profiler": {
            "enabled": True,
        },
    }
)

app.run()
```

Application configuration is divided broadly into:

```text
app
backend
engine
settings
profiler
```

Game-specific settings can be registered through the settings registry and made available to scenes as shared resources.

## Explore the examples

The repository contains three broad groups of examples:

```text
examples/
├── fundamentals/
├── experiments/
└── games/
```

### Fundamentals

Focused examples progressively introduce engine concepts.

Current areas include:

```text
backend
running
scenes
ECS
multiple scenes
shared scene settings
transforms
graphics
rendering
movement
collisions
bounds
lifecycle
UI
```

### Experiments

Experiments are used to stress or explore engine architecture before functionality becomes a stable reusable feature.

They may intentionally contain more complex or less polished code than the fundamentals.

### Games

Larger game examples demonstrate how several Tatuy features work together.

## Repository layout

```text
.
├── src/
│   ├── tatuy/
│   │   ├── app.py
│   │   ├── backend/
│   │   ├── engine/
│   │   ├── ecs/
│   │   ├── scenes/
│   │   ├── features/
│   │   ├── geometry/
│   │   ├── graphics/
│   │   ├── input/
│   │   ├── events/
│   │   ├── window/
│   │   ├── audio/
│   │   ├── capture/
│   │   ├── ui/
│   │   └── tooling/
│   │
│   ├── tatuy_cli/
│   ├── tatuy_mcp/
│   └── tatuy_profiler/
│
├── examples/
│   ├── fundamentals/
│   ├── experiments/
│   └── games/
│
├── docs/
├── tests/
├── AGENTS.md
├── CHANGELOG.md
├── manage.py
└── pyproject.toml
```

### `tatuy`

The engine and game-building APIs.

### `tatuy_cli`

Repository tooling, including commands used to discover and run examples.

### `tatuy_mcp`

Read-only development tooling that exposes configured Tatuy projects to MCP-compatible clients.

It is intended to help development assistants inspect the engine and game code while working with Tatuy.

### `tatuy_profiler`

Local tooling for inspecting profiles generated by the engine profiler.

## Design direction

Tatuy currently follows a few guiding principles.

### Keep gameplay in Python

Game rules should remain easy to write, inspect, and iterate on.

### Separate engine mechanics from game rules

Reusable capabilities such as movement integration, collision detection, lifecycle processing, and rendering belong in the engine.

Rules such as enemy behavior, scoring, wave progression, and power-ups belong in the game.

### Make frame execution explicit

System phases and ordering should make it possible to understand exactly when game behavior occurs.

### Defer structural mutations

Entity creation, removal, and other ECS structural changes should happen at well-defined synchronization points rather than unpredictably during iteration.

### Prefer composition

Entities gain behavior by combining small components and reusable systems rather than through deep object hierarchies.

### Keep backend-specific behavior isolated

Pygame is currently the only implemented backend, but game code should depend on Tatuy's engine abstractions rather than Pygame directly whenever practical.

## Current scope

Tatuy is not yet intended to compete with mature general-purpose engines.

Current priorities are:

- robust 2D ECS gameplay
- explicit system scheduling
- reusable gameplay features
- increasingly complex game prototypes
- profiling and debugging
- backend abstraction
- clean Python game code

Pygame remains the current backend.

The engine architecture is being designed so that performance-sensitive implementation details can evolve independently from game systems as Tatuy grows.

## Development

Install dependencies:

```bash
poetry install
```

Run an example:

```bash
poetry run python manage.py run example scenes.on_present
```

Run tests:

```bash
poetry run pytest
```

Formatting and static-analysis configuration lives in `pyproject.toml`.

The project currently uses:

- Black
- isort
- mypy
- pylint
- pytest

## Documentation

Documentation currently lives under:

```text
docs/
```

and focused working examples under:

```text
examples/fundamentals/
```

Because Tatuy is evolving quickly, the implementation is the source of truth when documentation and code disagree.

Start by exploring the fundamental scene, ECS, movement, collision, bounds, and lifecycle examples to understand how the pieces fit together.

## License

Tatuy is licensed under the MIT License.

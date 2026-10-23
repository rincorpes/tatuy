# Public API Map

Use this page to choose an existing Tatuy mechanism before proposing a new one.

The canonical boundary between normal game-authoring APIs and implementation details is defined in [Game authoring contract](../architecture/game-authoring-contract.md). This map helps locate existing mechanisms; it does not imply that every current deep import path is a stable public API.

## Canonical import layers

Use domain facades for normal game code:

```python
from tatuy import TatuyApp
from tatuy.ecs import World, GameSystem, EntityFactory
from tatuy.engine import SystemRegistration
from tatuy.scenes import Scene, Intent, SceneRegistry, SceneTickContext
from tatuy.features.movement import Movement, Velocity
from tatuy.features.collision import CollisionFrame, ColliderAccess
from tatuy.features.visual import Rect, RectBlueprint
from tatuy.ui import UiNode
```

The root `tatuy` package is intentionally small. It exposes the application entry point and application configuration contract, not the entire engine.

Deep implementation modules remain available to engine contributors, but normal games should not import runtime/bootstrap internals, ECS storage implementations, render compiler/executor internals, Python reference kernels, or concrete backend implementations unless the code is explicitly teaching or extending those internals.

`ColliderAccess` is an intentional collision extension API because game systems use it to inspect semantic collider geometry without depending on collision kernel implementations.

## Start a game

```text
TatuyApp
```

## Define a screen/game state

```text
Scene
SceneRegistry
```

## Scene-wide state

```text
World resource
Scene.resources()
shared_resource_types
```

## Entity construction

```text
EntityFactory
EntityBlueprint
SpawnDefinition
```

## Runtime spawning/despawning

```text
LifecycleQueue
```

## Add/remove component structure safely

```text
StructuralCommandBuffer
AddComponent
RemoveComponent
```

## Gameplay behavior

```text
GameSystem
```

## One-phase reusable processor

```text
BaseSystem
```

## Raw input → game action

```text
Intent
```

## Render ECS visual

```text
visual component + Transform
```

## Direct transient rendering

```text
Canvas
RenderQueue
```

## Game audio

```text
AudioService
```

## Engine/runtime action

```text
engine command
```

## Performance instrumentation

```text
profiler.span
profiler.metric
```

---

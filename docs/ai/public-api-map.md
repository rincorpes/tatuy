# Public API Map

Use this page to choose an existing Tatuy mechanism before proposing a new one.

The canonical boundary between normal game-authoring APIs and implementation details is defined in [Game authoring contract](../architecture/game-authoring-contract.md). This map helps locate existing mechanisms; it does not imply that every current deep import path is a stable public API.

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

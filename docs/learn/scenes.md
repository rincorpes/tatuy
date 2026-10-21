# Scenes

A scene represents one active part of a Tatuy game.

Examples:

- gameplay
- title screen
- pause overlay
- inventory
- debug screen

Conceptually:

```text
Scene
├── World
├── Intent
├── Tick context
├── Entity factory
├── Resources
├── Spawn definitions
├── Initial entities
├── Game systems
└── Lifecycle hooks
```

## Scene types

A typical scene declares:

```python
class MainScene(Scene[GameWorld, GameIntent, GameContext]):
    world_type = GameWorld
    intent_type = GameIntent
    tick_context_type = GameContext
    factory_type = GameFactory
```

## Configuration

Before `on_enter()`, the base scene configures shared infrastructure.

It:

- creates camera and screen effect helpers
- adds shared resources
- adds scene resources
- creates structural commands
- ensures lifecycle resources exist
- registers spawn definitions
- queues initial entities
- configures optional bounds resources

## Resources

```python
def resources(self, ctx):
    return (
        Score(),
        CollisionFrame(),
    )
```

## Spawn definitions

```python
def spawn_definitions(self, ctx):
    return {
        "enemy": SpawnDefinition("enemy"),
    }
```

## Initial entities

```python
def entities(self, ctx):
    yield EntitySpawn("player")
```

Initial entities use the normal lifecycle pipeline.

## Game systems

```python
def game_systems(self, ctx):
    return (
        PlayerSystem(),
        EnemySystem(),
    )
```

## Built-in overrides

Advanced scenes can remove a built-in:

```python
def builtin_overrides(self, ctx):
    return {
        "collision_detection": None,
    }
```

or replace its registration.

## Bounds

```python
def bounds(self, ctx):
    return Bounds(...)
```

Tatuy then adds world-bounds infrastructure automatically.

## Lifecycle hooks

### `on_enter(ctx)`

Scene-specific setup.

### `on_tick(ctx)`

Scene-level update glue.

### `on_present(ctx)`

Direct scene presentation.

### `on_exit()`

Cleanup when the scene is removed.

## Scene stack

Each scene entry has a policy controlling:

- update blocking
- input blocking
- opacity
- input reception

This allows overlays such as pause menus without forcing every scene into one global mode.

---

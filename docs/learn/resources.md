# Resources and Feature Composition

Resources are values stored once per world by type. They represent scene/world state rather than per-entity state.

Typical resources include:

```text
Score
WaveState
CollisionFrame
LifecycleQueue
GameSettings
UIFrame
```

## Scene-declared resources

A scene declares game-owned resources through `resources()`:

```python
class GameScene(Scene):
    def resources(self, ctx):
        return (
            Score(),
            WaveState(),
        )
```

The default runtime initializer adds those resources before `on_enter()`.

Read them from the world by type:

```python
score = self.world.get_resource(Score)
```

or from a system context:

```python
score = ctx.world.get_resource(Score)
```

A world cannot contain two resources of the same concrete type.

## Shared application resources

Application-level values may be shared into scene worlds with:

```python
shared_resource_types = (GameSettings,)
```

Runtime composition resolves each requested type from `SceneContext.resources` and adds it to the scene world before `on_enter()`.

Use this for application-owned configuration/state that multiple scenes intentionally share.

## Feature-owned resources

Some reusable features require runtime-owned resources. Examples include collision frames, lifecycle queues/registries, bounds frames, and UI layout/interaction state.

Game scenes should declare feature intent through the supported Scene hooks or public feature API rather than recreating default bootstrap behavior.

For example:

```python
def bounds(self, ctx):
    return Bounds(...)
```

allows runtime composition to provision the corresponding bounds resources consistently.

Likewise `spawn_definitions()` and `entities()` describe lifecycle intent while the runtime provisions lifecycle plumbing.

## Resource or component?

Use a component when state belongs to one entity.

Use a resource when state belongs to the whole world/scene or coordinates behavior across entities.

A useful test is: if deleting one entity should delete the state, it is probably a component; if many systems/entities share one authoritative value, it is probably a resource.

## Composition boundary

```text
Scene declarations
      ↓
DefaultSceneInitializer
      ↓
world resources / feature services
      ↓
built-in activation + game systems
```

`Scene` owns declarations. `tatuy.engine.runtime` owns default provisioning policy. Feature packages own the meaning of their own resources.

## What is implementation detail?

Normal game code should not depend on `DefaultSceneInitializer`, resource-bootstrap helper ordering, or runtime activation predicate implementation.

## Native preservation contract

A replacement runtime must preserve:

- resource lookup by type
- duplicate-type rejection
- shared-resource availability before `on_enter()`
- scene-declared resource availability before `on_enter()`
- supported feature resources being provisioned at the same lifecycle point
- Scene hooks retaining their current meaning

## Examples

- `examples/fundamentals/004_ecs/001_resources/app.py`
- `examples/fundamentals/006_shared_scene_settings/app.py`
- `examples/fundamentals/012_bounds/001_behavior/app.py`
- `examples/fundamentals/013_lifecycle/`

See [Use resources](../guides/use-resources.md) and [Feature Composition Architecture](../architecture/feature-composition.md).

---
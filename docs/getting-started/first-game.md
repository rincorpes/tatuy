# Your First Tatuy Game

This creates one rectangle using Tatuy's normal scene, ECS, factory, and lifecycle APIs.

```python
from tatuy.app import TatuyApp
from tatuy.ecs.entity.factory import EntityFactory, RectBlueprint
from tatuy.ecs.world import World
from tatuy.features.lifecycle.resources import SpawnDefinition
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2
from tatuy.scenes.context import Intent, SceneTickContext
from tatuy.scenes.registry import SceneRegistry
from tatuy.scenes.scene import EntitySpawn, Scene


class GameWorld(World):
    pass


class GameIntent(Intent):
    pass


class GameContext(SceneTickContext[GameWorld, GameIntent]):
    pass


class GameFactory(EntityFactory):
    registry = {
        "rect": RectBlueprint,
    }


@SceneRegistry.implementation("main")
class MainScene(Scene[GameWorld, GameIntent, GameContext]):
    world_type = GameWorld
    intent_type = GameIntent
    tick_context_type = GameContext
    factory_type = GameFactory

    def spawn_definitions(self, ctx):
        return {
            "player": SpawnDefinition(
                "rect",
                make_kwargs=lambda: {
                    "position": Vec2(100, 100),
                    "size": Size(64, 64),
                    "color": (240, 240, 240),
                },
            )
        }

    def entities(self, ctx):
        yield EntitySpawn("player")

    def on_enter(self, ctx):
        pass


if __name__ == "__main__":
    TatuyApp().run()
```

## What happened?

The scene declared a spawn definition named `player`.

Its `EntitySpawn` was queued through Tatuy's lifecycle infrastructure.

At a structural commit:

```text
LifecycleQueue
    ↓
SpawnDefinition
    ↓
EntityFactory
    ↓
RectBlueprint
    ↓
Transform + Rect
```

During presentation, the built-in renderer recognizes the visual entity.

You did not manually add `RenderSystem`.

That is an important Tatuy pattern:

> Games describe their state and rules. Reusable engine behavior activates when the required state exists.

Next: [Scenes](../learn/scenes.md).

---

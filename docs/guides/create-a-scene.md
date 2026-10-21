# Create a Scene

Define game-specific types:

```python
class GameWorld(World):
    pass


class GameIntent(Intent):
    pass


class GameContext(SceneTickContext[GameWorld, GameIntent]):
    pass
```

Register the scene:

```python
@SceneRegistry.implementation("main")
class MainScene(Scene[GameWorld, GameIntent, GameContext]):
    world_type = GameWorld
    intent_type = GameIntent
    tick_context_type = GameContext

    def on_enter(self, ctx):
        pass
```

Ensure the module containing the registration decorator is imported before `TatuyApp.run()`.

Use additional scene hooks for:

```text
resources()
spawn_definitions()
entities()
game_systems()
bounds()
builtin_overrides()
```

---

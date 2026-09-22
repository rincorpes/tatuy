# Scenes

A running engine can open a window and advance frames. A scene tells it what to update and what to draw in those frames.

A scene owns a world and an intent, and it creates a context for each update or presentation call:

```text
InputFrame → Intent → on_tick(ctx) → on_present(ctx) → render queue → backend
                   ↘ World ↗
```

This is a useful place to keep the rules for one screen of a game. A title screen, a match, and a pause overlay can each be a scene. You do not need all three to draw your first rectangle.

## Register and start a scene

The default engine configuration starts a scene named `main`. Register a scene under that ID before calling `TatuyApp().run()`:

```python
from tatuy.scenes.registry import SceneRegistry
from tatuy.scenes.scene import Scene

@SceneRegistry.implementation("main")
class MainScene(Scene):
    ...
```

The module containing this class must be **imported before the engine starts**. A decorator in a module nobody imports cannot register anything, no matter how optimistic the decorator feels. Defining the class in the same `app.py` you run is one simple way to ensure that import happens.

The scene's `on_enter(ctx)` method runs when the scene is created. `on_exit()` runs when it is removed from the scene stack. Changing scenes creates a new scene instance, so ordinary scene state starts fresh.

## World, intent, and contexts

| Object | What it holds | Lifetime |
| --- | --- | --- |
| `World` | Scene state, entities, components, and resources. | One scene instance. |
| `Intent` | Game actions derived from an `InputFrame`. | One scene instance. |
| `SceneContext` | Runtime access such as viewport, audio, engine commands, and shared resources. | Shared by the running engine. |
| `SceneTickContext` | This call's `dt`, world, intent, canvas, render queue, and `SceneContext`. | Created for each update or presentation call. |

Declare the classes a scene should construct:

```python
class MainScene(Scene[MyWorld, MyIntent, MyTickContext]):
    world_type = MyWorld
    intent_type = MyIntent
    tick_context_type = MyTickContext
```

The `world` and `intent` properties construct their objects on first access. Your `MyWorld` should initialize any game state it needs, and `MyIntent.update_from(input_frame)` should translate the current input snapshot into actions your scene understands.

`SceneContext` and `SceneTickContext` are different on purpose. The former gives a scene access to runtime services; the latter also carries this frame's `dt`, world, intent, and drawing tools.

## Update, then present

For an active scene, the engine updates intent from input before calling `on_tick(ctx)`. Put state changes here. `ctx.dt` is elapsed seconds, so a speed expressed in pixels per second can be used as `speed * ctx.dt`.

Later in the same engine step, `on_present(ctx)` records drawing commands. Put calls to `ctx.canvas` or `ctx.render_queue` here. The engine creates a fresh render queue for presentation and executes those commands through its render pipeline. Drawing into the update call's queue will not appear in the presented frame.

```python
def on_tick(self, ctx):
    ctx.world.x += 120 * ctx.dt

def on_present(self, ctx):
    ctx.canvas.text(
        position=Vec2(ctx.world.x, 40),
        text="Hello, Tatuy",
    )
```

Scenes can also declare systems for control, simulation, and presentation. Start with the callbacks above; systems become useful when several entities need the same behavior.

The [scene examples](./examples.md) introduce these pieces one at a time. The [moving rectangle tutorial](../tutorials/moving_rectangle.md) combines them in a complete program.

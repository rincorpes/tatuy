# Make a Moving Rectangle

The [running examples](../002_running/examples.md) show how frames happen. The [scene examples](../003_scenes/examples.md) show where scene code runs. Here we put the two together: hold the left or right arrow key, and a rectangle moves across the window.

This tutorial uses `TatuyApp`, one registered scene, an intent, a world, and a canvas. There is no ECS system yet; one rectangle does not need a committee.

## Run it

From the repository root:

```bash
poetry install
poetry run python manage.py run example moving_rectangle
```

The complete source is in [`examples/fundamentals/004_moving_rectangle/app.py`](../../examples/fundamentals/004_moving_rectangle/app.py). Use the left and right arrow keys, or A and D, to move the rectangle. Close the window to stop.

## The complete program

```python
from __future__ import annotations

from tatuy.app import TatuyApp
from tatuy.ecs.world import World
from tatuy.geometry.size import Size
from tatuy.input.frame import InputFrame
from tatuy.input.keys import Key
from tatuy.math.vec2 import Vec2
from tatuy.scenes.context import Intent, SceneContext, SceneTickContext
from tatuy.scenes.registry import SceneRegistry
from tatuy.scenes.scene import Scene


BOX_SIZE = Size(48, 48)
SPEED = 240.0  # pixels per second


class MovingWorld(World):
    def __init__(self) -> None:
        super().__init__()
        self.position = Vec2(0, 0)


class MoveIntent(Intent):
    def update_from(self, input_frame: InputFrame) -> None:
        self.move_left = input_frame.is_down(Key.LEFT) or input_frame.is_down(
            Key.A
        )
        self.move_right = input_frame.is_down(
            Key.RIGHT
        ) or input_frame.is_down(Key.D)


class MoveContext(SceneTickContext[MovingWorld, MoveIntent]): ...


@SceneRegistry.implementation("main")
class MovingScene(Scene[MovingWorld, MoveIntent, MoveContext]):
    world_type = MovingWorld
    intent_type = MoveIntent
    tick_context_type = MoveContext

    def on_enter(self, ctx: SceneContext) -> None:
        self.world.position = Vec2(
            (ctx.viewport.virtual_w - BOX_SIZE.width) / 2,
            (ctx.viewport.virtual_h - BOX_SIZE.height) / 2,
        )

    def on_tick(self, ctx: MoveContext) -> None:
        direction = int(ctx.intent.move_right) - int(ctx.intent.move_left)
        new_x = ctx.world.position.x + direction * SPEED * ctx.dt
        max_x = ctx.scene_context.viewport.virtual_w - BOX_SIZE.width
        ctx.world.position.x = max(0, min(new_x, max_x))

    def on_present(self, ctx: MoveContext) -> None:
        ctx.canvas.rect(
            position=ctx.world.position,
            size=BOX_SIZE,
            color=(80, 190, 255),
        )


def main() -> None:
    TatuyApp().run()


if __name__ == "__main__":
    main()
```

## Follow one frame

1. `TatuyApp` builds the backend, engine, services, and loop. The engine starts the scene registered as `main`.
2. The input service produces an `InputFrame`. `MoveIntent.update_from` turns physical keys into the scene's `move_left` and `move_right` actions.
3. `on_tick` changes the position stored in `MovingWorld`. `SPEED * ctx.dt` converts pixels per second into pixels for this frame. The clamp keeps the rectangle inside the current viewport width.
4. `on_present` adds a rectangle to the canvas. The engine sends that drawing command through its render pipeline, and the backend draws it.

The world stores position because it has to survive from one frame to the next. The intent stores what the player wants **this** frame. Presentation reads the world; it does not move the rectangle again.

Try changing `SPEED`, `BOX_SIZE`, or the color. For a next step, put several objects in the world and give them components; then a system can update all of them with the same rule.

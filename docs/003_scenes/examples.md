# Scene Examples

The examples in this section build a scene one part at a time. Run them from the repository root; the CLI omits numeric directory prefixes from target names.

The first two examples intentionally have no tick context yet. The current engine prints `No tick content type defined` during their frames; example 3 adds that type.

## 1. A world and a registered scene

[Source: `001_world/app.py`](../../examples/fundamentals/003_scenes/001_world/app.py)

```bash
poetry run python manage.py run example scenes.world
```

`MyGameWorld` extends `World`, and `@SceneRegistry.implementation("main")` makes `MyGameScene` available under the engine's default start ID. The example supplies an empty intent because the engine updates scene intent each frame; the next example gives that intent something to do. `on_enter` prints when the scene starts. There is nothing to draw yet, so a blank window is expected.

## 2. An intent

[Source: `002_intent/app.py`](../../examples/fundamentals/003_scenes/002_intent/app.py)

```bash
poetry run python manage.py run example scenes.intent
```

`intent_type` tells the scene which intent to create. The engine calls its `update_from(input_frame)` before each update. This example prints from that method to show when the translation happens; a real intent would record actions such as `move_left`.

## 3. A tick context

[Source: `003_context/app.py`](../../examples/fundamentals/003_scenes/003_context/app.py)

```bash
poetry run python manage.py run example scenes.context
```

`tick_context_type` connects the scene's world and intent to `SceneTickContext`. The intent now stores whether the pointer is inside the window. The context lets `on_tick` and `on_present` read that same intent and world.

## 4. An update callback

[Source: `004_on_tick/app.py`](../../examples/fundamentals/003_scenes/004_on_tick/app.py)

```bash
poetry run python manage.py run example scenes.on_tick
```

`on_tick(ctx)` runs during the update stage. This example prints on every frame, so the terminal will be noisy until you close the window. That is a demonstration of the callback, not a recommended logging strategy for a finished game.

## 5. Input becomes intent

[Source: `005_build_intent/app.py`](../../examples/fundamentals/003_scenes/005_build_intent/app.py)

```bash
poetry run python manage.py run example scenes.build_intent
```

The intent copies `input_frame.mouse_inside` into its own `mouse_inside` action state. `on_tick` reads `ctx.intent.mouse_inside`. This is the boundary between device input and a scene's interpretation of it.

## 6. Presentation

[Source: `006_on_present/app.py`](../../examples/fundamentals/003_scenes/006_on_present/app.py)

```bash
poetry run python manage.py run example scenes.on_present
```

`on_present(ctx)` uses `ctx.canvas.text(...)` to draw whether the mouse is inside the window. The engine collects this command and sends it through the render pipeline after the update stage.

The [moving rectangle tutorial](../tutorials/moving_rectangle.md) uses the same pieces to make something respond to keyboard input and move at a speed measured per second.

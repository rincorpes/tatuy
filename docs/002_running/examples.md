# Running Examples

These four examples open an engine window with progressively less setup code. They focus on **who runs the engine**, so they do not register a scene. A blank window is expected; the engine may also print that no input scene exists. The [scene examples](../003_scenes/examples.md) add one.

Run them from the repository root with Poetry. The CLI uses the readable folder names and drops the numeric prefixes.

## 1. Engine with a manual loop

[Source: `001_engine/app.py`](../../examples/fundamentals/002_running/001_engine/app.py)

```bash
poetry run python manage.py run example running.engine
```

This example creates a Pygame backend and an `Engine`, then calls `engine.start()` and `engine.step(dt, frame_index)` itself. It measures `dt` with `perf_counter()`. After `step`, it sleeps for any time left in the target frame duration.

```python
frame_start = perf_counter()
dt = frame_start - previous_frame_start
previous_frame_start = frame_start

engine.step(dt, frame_index)

elapsed = perf_counter() - frame_start
if engine.running and elapsed < target_dt:
    sleep(target_dt - elapsed)
```

The sleep controls pacing; the measured `dt` tells the engine how much time actually passed. The loop checks `engine.running` because a quit event may stop the engine during `step`. Its `finally` block calls `engine.stop()`.

## 2. Engine with `PythonLoop`

[Source: `002_loop/app.py`](../../examples/fundamentals/002_running/002_loop/app.py)

```bash
poetry run python manage.py run example running.loop
```

`PythonLoop().run(engine)` owns the repeated calls to `start`, `step`, and `stop`. It also measures `dt` and aims for the requested frame rate. You still choose and construct the backend and engine.

## 3. `Runtime`

[Source: `003_runtime/app.py`](../../examples/fundamentals/002_running/003_runtime/app.py)

```bash
poetry run python manage.py run example running.runtime
```

`Runtime` stores an `Engine` and a `PythonLoop`. Its `run()` method delegates to the loop. It is a convenient bundle, not a second game loop hiding inside the first one.

## 4. `TatuyApp`

[Source: `004_app/app.py`](../../examples/fundamentals/002_running/004_app/app.py)

```bash
poetry run python manage.py run example running.app
```

`TatuyApp` builds the backend, runtime services, engine, and loop. Its defaults use the Pygame backend, the Python loop, and a starting scene named `main`. This is the usual entry point once your game has a registered scene.

The examples deliberately stop at the runtime boundary. Continue with [Scenes](../003_scenes/index.md) to see where input, updates, and drawing go.

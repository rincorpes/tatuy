# Use Audio

Game code uses Tatuy's scene audio service instead of calling backend audio objects directly.

## Configure sounds

Declare backend audio and named sounds in the app configuration:

```python
TatuyApp(
    {
        "backend": {
            "audio": {
                "enabled": True,
                "sounds": [
                    {"name": "laser", "path": "assets/laser.wav"},
                ],
            }
        }
    }
).run()
```

## Play from scene code

`SceneContext.audio` exposes the runtime audio adapter:

```python
class DemoScene(Scene):
    def on_enter(self, ctx):
        ctx.audio.play("laser")
```

The service also supports loading sounds, master volume, per-sound volume, loops, and stopping all sounds.

Normal game code should not import a concrete Pygame audio implementation. Backend-specific audio fundamentals may do so only when the backend itself is the lesson.

Example: `examples/fundamentals/018_audio/app.py`.

See also [Audio](../learn/audio.md).

---
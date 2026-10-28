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

`SceneContext.audio` exposes the runtime audio adapter. Loading can happen before browser audio unlocks; Tatuy defers the load until the device becomes ready. Trigger playback from normal game input so the same code works on desktop and browser hosts:

```python
class DemoScene(Scene):
    def on_enter(self, ctx):
        ctx.audio.load_sound("laser", ctx.assets.path("assets/laser.wav"))

    def on_tick(self, ctx):
        if ctx.intent.fire_pressed:
            ctx.scene_context.audio.play("laser")
```

Browser builds keep target audio configuration but force `auto_init: false`. The first key or pointer-button press unlocks enabled audio before scene update, so gameplay does not need browser-specific code.

The service also supports master volume, per-sound volume, loops, stopping all sounds, and `set_muted()` / `toggle_muted()`. `AudioService.ready` and `AudioService.last_error` can be shown in diagnostics or an audio-settings UI.

Normal game code should not import a concrete Pygame audio implementation. Backend-specific audio fundamentals may do so only when the backend itself is the lesson.

Example: `examples/fundamentals/018_audio/app.py`.

See also [Audio](../learn/audio.md).

---
# Use Camera Effects

Camera effects are scene-owned presentation state provided by Tatuy's default runtime composition.

Normal game code accesses the scene's `camera_fx` service rather than constructing backend-specific camera objects.

## Start a shake

```python
class HitScene(Scene):
    def on_enter(self, ctx):
        self.camera_fx.shake(duration=0.25, strength=8.0)
```

A scene can trigger the effect directly when gameplay events occur; game-specific systems can route their events back through scene-owned feature state when needed. The engine advances the effect each frame and snapshots its `ViewTransform` during presentation.

`CameraFX` uses linear decay and combines overlapping shake requests by keeping the strongest active strength/duration.

## Ownership

`CameraFX` belongs to `tatuy.features.fx`. `ViewTransform` remains a low-level graphics value. This keeps effect policy above the graphics layer while allowing the render pipeline to consume backend-agnostic view data.

Example: `examples/fundamentals/016_camera_effects/app.py`.

See also [Effects](../learn/effects.md).

---
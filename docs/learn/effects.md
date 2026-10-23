# Effects

Tatuy's FX feature owns reusable game/presentation effects rather than putting effect policy inside graphics.

Public FX concepts live under:

```python
from tatuy.features.fx import (
    CameraFX,
    Particle,
    ParticleEmitter,
    ParticleUpdateSystem,
    ScreenEffectStack,
    Trail,
    TrailRenderSystem,
    TrailSystem,
)
```

## Particles

`ParticleEmitter` creates particle entities using engine-facing data and an injectable random source. Capacity limits make emission bounded and deterministic tests possible when a seeded RNG is supplied.

`ParticleUpdateSystem` advances particle lifetime and movement. Particle presentation remains semantic render work rather than backend drawing.

## Trails

A `Trail` records recent transform positions. `TrailSystem` updates trail history and `TrailRenderSystem` submits presentation work.

Trail lifetime, sampling interval, radius, and maximum retained points define its visible history and memory bound.

## Camera effects

`CameraFX` is scene-owned runtime state. Game code triggers effects such as shake; Tatuy updates the effect and snapshots a backend-agnostic `ViewTransform` during presentation.

The effect policy belongs to `features.fx`; the resulting view transform belongs to graphics.

## Screen effects

`ScreenEffectStack` owns active screen effects such as `FlashEffect` and produces low-level screen-overlay data for presentation.

Screen-effect policy stays outside the graphics layer while the render pipeline consumes only semantic overlay data.

## Phase contract

Effects may span multiple phases:

```text
game event / emission
        ↓
simulation state update
        ↓
presentation submission
```

A `GameSystem` is appropriate when one game-specific effect behavior needs callbacks in several phases. Reusable generic behavior belongs in the feature systems.

## What is implementation detail?

Game code should not depend on:

- backend draw calls
- render executor implementation
- internal particle/trail kernel representation
- how camera transforms are applied inside the executor
- how overlays are encoded for a future native renderer

## Native preservation contract

A replacement implementation must preserve:

- particle emission semantics and capacity behavior
- deterministic behavior when the same RNG/input is supplied
- trail aging, sampling, and capacity behavior
- camera-effect timing and resulting view-transform semantics
- screen-effect timing and overlay semantics
- semantic render ordering produced by effect presentation systems

## Examples

- `examples/fundamentals/014_particles/app.py`
- `examples/fundamentals/015_trails/app.py`
- `examples/fundamentals/016_camera_effects/app.py`
- `examples/fundamentals/017_screen_effects/app.py`

Related guides:

- [Add particles](../guides/add-particles.md)
- [Use trails](../guides/use-trails.md)
- [Use camera effects](../guides/use-camera-effects.md)
- [Use screen effects](../guides/use-screen-effects.md)

---
# Entities: Shatterphase

This experiment ports Shatterphase into Tatuy's scene configuration hooks and
`GameSystem` lifecycle. It runs entirely from this directory; the original game
checkout is not required.

From the repository root:

```bash
poetry run python manage.py run experiment entities
```

Move with **WASD**, launch with **Space** or **left click**, and hold **right click**
to aim. The player is a circle with an attached rectangle shield. Balls rest on
the shield until launched. Both player shapes bounce flying balls.

The port includes all twenty waves, regular hex enemies with polygon collisions,
multi-hit damage, ghost and explosive transformations, descent, combos and score,
ball spin and curvature, minimum bounce angles, side wrapping, particles, trails,
shake, flash, aiming previews, lives, and delayed ball respawns. The seven original
pickups are available: wide shield, fast, slow, multiball, extra life, sticky, and
floor shield.

`app.py` contains application configuration. The `settings.breakout` section keeps
the original game's configuration names: `player` controls the circle's radius and
speed, `paddle` controls the attached shield, and `bricks` controls enemy damage and
transformations. The shield is rectangular by default; `paddle.curved` retains the
original curved paddle option. As in the original settings, `persistent_balls`
defaults to `true`; set it to `false` for an open floor and life loss.

`scene.py` declares resources, bounds, spawn definitions, initial entities, and
game systems. The engine supplies movement, attachments, collision response,
lifetimes, rendering, and structural commit barriers. `systems.py` implements game
rules, with collision detection limited to gameplay pairs to keep dense hex waves
fast. `entities.py` owns blueprints, `aiming.py` predicts circle sweeps against hex
edges and corners, and `waves.py` contains the twenty wave definitions.

Run the integration checks without opening a window:

```bash
poetry run python -m pytest examples/experiments/002_entities/test_game.py -q
```

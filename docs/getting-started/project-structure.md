# Project Structure

Tatuy does not require one mandatory project layout.

A useful starting point is:

```text
my_game/
├── app.py
├── settings.py
├── scenes/
├── entities/
├── systems/
├── resources/
└── assets/
```

## `app.py`

Application composition:

```text
TatuyApp
configuration
scene imports
application start
```

## `scenes/`

Scene composition and scene-specific setup.

## `entities/`

Entity blueprints, identity components, and construction helpers.

## `systems/`

Game-specific behavior such as:

```text
PlayerSystem
EnemySystem
WaveSystem
CombatSystem
```

## `resources/`

Scene-wide game state.

## `settings.py`

Game configuration and registered settings builders.

## `assets/`

Textures, fonts, sounds, and other game data.

## Keep architecture proportional

A prototype may be one file.

That is fine.

Split code when responsibilities become difficult to understand, not because an engine template says every game needs twelve directories.

---

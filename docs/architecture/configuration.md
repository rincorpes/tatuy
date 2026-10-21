# Configuration Architecture

Tatuy configuration has several layers.

```text
TatuyApp config
├── app
├── backend
├── engine
├── settings
└── profiler
```

## Application configuration

Selects application composition such as backend and loop.

## Backend configuration

Belongs to the selected backend implementation.

## Engine configuration

Controls engine-level runtime behavior such as start scene, FPS target, and debug overlay.

## Settings

Named game/runtime settings sections are built through `SettingsRegistry`.

## Profiler configuration

Controls profiling behavior independently from game settings.

The layers should remain separate so game configuration does not become coupled to platform configuration.

---

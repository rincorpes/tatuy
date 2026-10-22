# Pygame Backend

Pygame implements all six backend capabilities under
`src/tatuy/backend/pygame/`.

| Module | Responsibility |
| --- | --- |
| builder.py | Registry registration and concrete configuration decoding |
| pygame_backend.py | Platform initialization and capability composition |
| components/events.py | Native-event filtering and Tatuy event payloads |
| components/window.py | Display creation, title, resize, SDL wrapper lifetime |
| components/input.py | Pointer observation and system cursor selection |
| components/renderer.py | Shapes, fonts, textures, clipping, frame presentation |
| components/audio.py | Mixer setup, sound loading, playback, and volume |
| components/capture.py | Surface saving and BGRA extraction |

Configuration and renderer/window/capture wiring are described in
[Configuration](../configuration.md) and [Lifecycle](../lifecycle.md).
Backend-level examples are in `examples/fundamentals/001_backend/`.

## Tests

The backend test layout mirrors source under
`tests/src/tatuy/backend/`, including `pygame/components/`.

```bash
poetry run python -m pytest tests/src/tatuy/backend -q -rxX
poetry run python -m mypy src/tatuy/backend
poetry run python -m pylint src/tatuy/backend
```

Unit tests use mocks and offscreen surfaces. Texture upload tests substitute
display-dependent conversion while checking row repacking and output pixels.
They do not prove native display, mixer/device, font-file, or driver behavior.

Strict expected-failure regression tests identify pending implementation
issues by review ID. They must be revisited when the associated behavior is
fixed; an unexpected pass fails the suite.

## Current constraints

- Pygame initialization/shutdown is global; backend instances are not isolated.
- Initialization failures roll back platform state; see the lifecycle page for cleanup retry semantics.
- Input configuration flags and capture configuration fields are not enforced
  in the corresponding Pygame ports.
- See the capability pages for audio volume, text defaults, and tiled
  texture/alpha polygon limitations.


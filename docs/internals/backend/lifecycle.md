# Backend Lifecycle

## Construction and initialization

`BackendFactory.create(name, config)` builds a backend without calling
`init()`. Direct `PygameBackend(config)` construction stores configuration,
creates a shared `ViewportTransform`, and sets `initialized=False`.
Capability attributes are assigned by `init()`, not by construction.

Pygame initialization currently performs these steps:

1. If audio is enabled, call `pygame.mixer.pre_init()` with the configured
   frequency, channel count, and buffer size.
2. Call `pygame.init()`.
3. Construct events, window, and input capabilities.
4. Construct the renderer with the window and shared viewport transform.
5. Construct audio; call its `init()` if enabled and `auto_init=True`.
6. Construct capture with the same window.
7. Set `initialized=True`.

`pygame.init()` initializes imported Pygame modules, so audio flags should
not be interpreted as a guarantee that Pygame never touches the mixer.

## Window opening and runtime use

`backend.window.open()` is separate. It creates the display surface, sets
the caption, retains the SDL window wrapper, and obtains window position.
Drawing, window size, capture, and texture conversion require an open display
or an appropriate test surface.

The normal engine path is `Engine.start()`: initialize the backend, open
the window through `WindowService`, initialize the viewport, then start
the scene. Do not use `initialized` as a synonym for "window is open".

For direct backend usage:

```python
from tatuy.backend.pygame import PygameBackend, PygameBackendConfig

backend = PygameBackend(PygameBackendConfig())
try:
    backend.init()
    backend.window.open()
    backend.renderer.begin_frame()
    backend.renderer.end_frame()
finally:
    backend.stop()
```

Interactive examples must also poll events regularly.

## Shutdown and current failure behavior

`stop()` returns immediately when `initialized=False`. Otherwise it calls
`pygame.quit()` and clears the flag. Stopping before initialization and
repeated stopping are safe. Shutdown affects Pygame globally, so independent
simultaneous backends do not have isolated platform lifetimes.

There is currently no repeated-init guard. Reinitializing replaces capability
objects and their caches. If initialization fails after `pygame.init()`,
the flag remains false and `stop()` does not release partially initialized
resources. Cleanup on partial failure is an open implementation issue.

At the loop level, `PythonLoop.run()` calls `engine.start()` before its
`try/finally`; startup exceptions therefore also bypass normal loop cleanup.
Successful execution stops through `Engine.stop()`, which closes capture
before stopping the backend.


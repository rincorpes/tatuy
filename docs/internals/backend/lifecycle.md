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

## Shutdown and failure behavior

Repeated successful `init()` calls are no-ops, preserving capabilities and
caches. Failures during platform initialization or capability setup attempt
`pygame.quit()`. The original error propagates; if rollback also fails,
the cleanup error is chained as its cause.

`stop()` is safe before initialization and after successful cleanup.
It clears `initialized` before quitting. If quitting raises, cleanup remains
pending and `stop()` can retry. Until cleanup succeeds, `init()` raises.
After cleanup succeeds, initialization may be attempted again.
Capabilities remain referenced through quitting, preserving SDL window
wrapper lifetime protection. Do not use capabilities after stopping or
failed initialization.

`PythonLoop.run()` includes startup and frame-clock construction in its
cleanup boundary. Backend, window, and scene startup failures therefore call
`Engine.stop()`, which closes capture before stopping the backend.
Engine cleanup tracks capture and backend shutdown independently from
`running`. A failed stage remains pending, so another `Engine.stop()` retries
it without repeating stages that already succeeded. Backend cleanup is still
attempted if capture closing fails. Event subscriptions are cleared in a
`finally` block even when either cleanup stage raises, including interruption
exceptions. Calling `stop()` before startup or after successful cleanup is a
no-op. `start()` rejects a stopped engine with pending cleanup; finish cleanup
with `stop()` first. If both cleanup stages fail, the backend error propagates
with the capture error preserved as exception context.

Startup or execution errors remain primary if cleanup also fails; the cleanup
error is chained as the cause. Cleanup errors after normal exit propagate
directly. Interruption exceptions follow the same cleanup rules.

Pygame initialization/shutdown is global; simultaneous backend instances do
not have isolated platform lifetimes.


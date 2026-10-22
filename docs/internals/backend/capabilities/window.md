# Window Capability

`WindowService` exposes runtime window operations. The Pygame window owns
its native surface and SDL wrapper; the shared `Window` protocol exposes
no native `screen`. Renderer/capture implementations use their concrete
Pygame window internally.

`open()` creates the display, applies title/flags, reads position, and
retains `_sdl_window`. Native events borrow its pointer, so the wrapper
must remain alive through display shutdown.

`size` reads the live display-surface size. `set_title()` changes the title.
`resize(width, height)` is an explicit request and calls `set_mode()`.
`sync_size(width, height)` observes a native notification and refreshes the
surface reference without calling `set_mode()` or replacing the SDL wrapper.

The Windows desktop probe confirmed that the display surface already has
the new dimensions when native size-change notifications are delivered.
`WindowService.sync_events()` therefore calls `sync_size()`, not `resize()`.
The service caches its previous observed size from `open()` for emitted
old/new-size data. Duplicate native notifications do not request a resize.
Move/minimize/maximize/restore/close notifications update service state.

Configuration stays frozen; title/resize operations do not rewrite it.
Opening again uses configured values. Backend shutdown closes the platform;
there is no independent window close method.

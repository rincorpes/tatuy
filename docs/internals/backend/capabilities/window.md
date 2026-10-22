# Window Capability

Runtime code normally uses `WindowService`. The Pygame port owns the
display surface and the SDL window wrapper.

Construction stores configuration and resize flags without opening a display.
`open()` creates the configured surface using `pygame.display.set_mode`,
sets the configured caption, and reads window position into a Tatuy `Vec2`.
The SDL wrapper is kept in `_sdl_window`: native window events borrow its
pointer, so retaining it is necessary for lifetime safety.

`size` reads the current surface dimensions into `Size`. It is unavailable
before a surface has been created. `set_title(title)` updates the caption
and cached title. `resize(width, height)` calls `set_mode` with the original
resize flags and updates the screen reference.

`WindowService.sync_events()` updates position/minimized/maximized/close
state and emits higher-level notifications. Resize events currently call
the port's resize method. This can invoke `set_mode` for notifications
about a size Pygame has already applied; native resize behavior should be
checked before changing that policy.

The configuration stays frozen: resizing/title changes do not rewrite it.
Calling `open()` again uses the original configured title/dimensions.
The port has no independent close operation; backend shutdown uses
`pygame.quit()`.


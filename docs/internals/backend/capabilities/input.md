# Input Capability

The backend protocol exposes `get_pointer_state()` and `set_cursor()`.
Keyboard/button event state is assembled by higher-level `InputService`
and `InputFrame`, not by this pointer port.

`PygameInput.get_pointer_state()` returns integer window-space coordinates.
Its `inside` flag requires all of:

- an existing display surface;
- mouse focus;
- a point inside the surface rectangle.

The right and bottom edges are exclusive. Position is still returned when
the pointer is outside or there is no surface. No viewport conversion is
performed here.

`set_cursor()` maps `Cursor.ARROW`, `HAND`, and `TEXT` to Pygame system
cursors. A successful selection is cached; repeated selections avoid another
native call. Failed native calls propagate and do not update that cache.

The current `enable_keyboard`, `enable_mouse`, and `enable_gamepad`
configuration flags do not enable or disable these operations. Gamepad
support is not implemented by this port.


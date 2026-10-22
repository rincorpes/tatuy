# Input Capability

`get_pointer_state()` observes the pointer in window coordinates;
`set_cursor()` selects a system cursor. No viewport conversion happens here.
Keyboard/button state is assembled by `InputService`, not the pointer port.

`enable_keyboard=False` suppresses key and text events and publishes no held,
pressed, or released keys. `enable_mouse=False` suppresses mouse events,
pointer polling and cursor changes; snapshots have neutral mouse state.
Disabled devices clear previously held state without synthesizing releases.
The event collector and input service both honor these flags. Window and
quit events remain available even when both input devices are disabled.

Pygame gamepad support is not implemented. `enable_gamepad=True` raises
`NotImplementedError` before backend initialization acquires platform state.
The shared configuration retains the flag for backends supporting controllers.

An enabled pointer is inside only when a display exists, the mouse has focus,
and its coordinates lie inside the surface. Right/bottom edges are exclusive.
Position is still reported outside the display. Disabled pointers return
`PointerState(position=(0, 0), inside=False)` without native calls.

Cursor choices are ARROW, HAND, and TEXT. Successful choices are cached;
native errors propagate without updating the cache.

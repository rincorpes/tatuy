# Events Capability

`get_events()` drains the Pygame event queue, translates recognized native
events to Tatuy `Event` objects, and preserves their order.
Each event has a category, type, lowercase type name, and attribute dictionary.
Polling and translation have separate profiler spans.

| Native event | Tatuy payload |
| --- | --- |
| KEYDOWN / KEYUP | key: Tatuy Key |
| TEXTINPUT | text: string |
| MOUSEMOTION | pos and rel: integer pairs |
| MOUSEBUTTONDOWN / MOUSEBUTTONUP | button: integer; pos: integer pair |
| MOUSEWHEEL | x and y: floats |
| Window move/resize/size-change/minimize/maximize/restore/close; QUIT | Copy of native attributes |

Keyboard mapping includes letters A–Z, digits, F1–F12, arrows, Escape,
Enter, Space, Tab, Backspace, and Delete. Unmapped keys are dropped;
modifier keys, keypad variants, and gamepad input are not comprehensively
supported. Unknown native event types are dropped.

Key events retain only `key`; native modifier/repeat metadata is discarded.
Mouse coordinates remain window coordinates here. Higher layers manage
input-frame state and coordinate interpretation.

Window payloads are copied unchanged and may contain Pygame-specific values.
This is a remaining portability boundary to assess before adding another
backend. Input enable flags are not applied by event translation.


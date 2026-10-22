# Events Capability

`get_events()` drains the native queue and emits supported Tatuy events in
order. Polling and translation have separate profiler spans.

| Event | Tatuy attributes |
| --- | --- |
| KEYDOWN / KEYUP | key: Tatuy Key |
| TEXTINPUT | text: string |
| MOUSEMOTION | pos and rel: integer pairs |
| MOUSEBUTTONDOWN / MOUSEBUTTONUP | button: integer; pos: integer pair |
| MOUSEWHEEL | x and y: floats |
| Window moved/resized/size changed | x and y: integers |
| Window minimized/maximized/restored/close; QUIT | Empty dictionary |

Native window wrappers and arbitrary native attributes are not exported.
Keyboard mapping covers letters, digits, F1-F12, arrows, common control
keys, left/right Shift/Ctrl/Alt/GUI, and numeric keypad digits/operators.
Modifier state is represented by held keys; native modifier/repeat metadata
is not copied. Unknown keys/events are dropped. Gamepad input is unsupported.

The backend passes its input configuration to the event collector. Direct
`PygameEvents(config, input_config=None)` construction defaults to enabled
keyboard and mouse. Disabled keyboard also suppresses text input; disabled
mouse suppresses motion/buttons/wheel. Window/quit events are never filtered
by device flags. Coordinates remain in window space.

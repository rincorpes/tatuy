# Events

The `Events` capability collects platform events and converts them into Tatuy events.

The public API is intentionally small:

```python
events = backend.events.get_events()
```

A backend-specific event should not escape into the rest of the engine unchanged.

For example:

```text
pygame.KEYDOWN
       ↓
PygameEvents
       ↓
Tatuy Event
```

The Pygame backend converts keyboard events into Tatuy's `Key` enum.

Conceptually:

```python
Event(
    category=EventCategory.INPUT,
    type=EventType.KEYDOWN,
    attrs={
        "key": Key.SPACE,
    },
)
```

This means systems consuming events do not need to know what:

```python
pygame.K_SPACE
```

is.

And a future backend does not need to pretend it is Pygame just to keep the engine happy.

---

## Supported event categories

Events are currently divided into categories such as:

```text
INPUT
WINDOW
```

Input events include things such as:

- KEYDOWN
- KEYUP
- TEXTINPUT
- MOUSEMOTION
- MOUSEBUTTONDOWN
- MOUSEBUTTONUP
- MOUSEWHEEL

Window events include things such as:

- WINDOWMOVED
- WINDOWRESIZED
- WINDOWSIZECHANGED
- WINDOWMINIMIZED
- WINDOWMAXIMIZED
- WINDOWRESTORED
- WINDOWCLOSE
- QUIT

Unsupported native events are ignored by the backend. Not every event deserves to become everybody else's problem, at least not now.


# Backend Lifecycle

A backend has a small lifecycle:

```text
Construct
   ↓
init()
   ↓
Components available
   ↓
Run
   ↓
stop()
   ↓
Platform resources released
```

A basic Pygame backend can be created like this:

```python
from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)


def main():
    backend = PygameBackend(
        config=PygameBackendConfig()
    )

    backend.init()

    # Use backend...

    backend.stop()
```

## Construction

Creating the object:

```python
backend = PygameBackend(
    config=PygameBackendConfig()
)
```

Stores the configuration and creates backend-level state such as the viewport transform.

At this point, backend components such as the renderer, audio system, input system, and capture system have not been constructed yet.

This is intentional, instantiation should not suddenly open windows, initialize audio devices, contact the spirits, or otherwise surprise the caller.

---

## Initialization

Calling:

```python
backend.init()
```

initializes Pygame and constructs the backend capabilities:

```text
Events
Window
Input
Renderer
Audio
Capture
```

The audio subsystem is also initialized when audio is enabled.

### Opening the window

Currently, window creation is an explicit operation:

```python
backend.window.open()
```

So a minimal backend capable of rendering looks like:

```python
backend = PygameBackend(
    PygameBackendConfig()
)

backend.init()
backend.window.open()
```

This distinction matters:

```text
backend.init()
```

prepares the backend and its components.

```text
backend.window.open()
```

creates the actual game window.

---

## Shutdown

When the backend is no longer needed:

```python
backend.stop()
```

platform resources are released and the backend returns to an uninitialized state.

Calling `stop()` on an already stopped backend is safe:

```python
if not self.initialized:
    return
```

This is useful during shutdown paths, where things tend to happen in whatever order the universe considers funniest.

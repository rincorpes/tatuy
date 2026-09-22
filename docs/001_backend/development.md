# Creating a Custom Backend

A custom backend needs to satisfy Tatuy's `Backend` protocol.

That means providing implementations for:

```text
Events
Window
Input
Renderer
Audio
Capture
```

and exposing them through a backend object.

A typical backend package might look like:

```text
tatuy/
└── backend/
    └── mybackend/
        ├── __init__.py
        ├── builder.py
        ├── config.py
        ├── backend.py
        └── components/
            ├── events.py
            ├── window.py
            ├── input.py
            ├── renderer.py
            ├── audio.py
            └── capture.py
```

---

## Step 1: Create backend configuration

```python
from dataclasses import dataclass

from tatuy.backend.config import BackendConfig


@dataclass(frozen=True)
class MyBackendConfig(BackendConfig):
    name: str = "mybackend"
```

Backend-specific capability configuration can also be added when required.

---

## Step 2: Implement capabilities

For example:

```python
class MyWindow:
    ...

class MyRenderer:
    ...

class MyInput:
    ...
```

These classes do not need to inherit from Tatuy protocols. Python protocols use structural typing. If the object provides the required interface, it satisfies the protocol. Duck typing, except the duck has type hints and CI will yell at you.

---

## Step 3: Compose the backend

```python
class MyBackend:
    def __init__(
        self,
        config: MyBackendConfig,
    ):
        self.config = config
        self.viewport_transform = (
            ViewportTransform()
        )
        self.initialized = False

    def init(self):
        self.events = MyEvents(...)
        self.window = MyWindow(...)
        self.input = MyInput(...)
        self.renderer = MyRenderer(...)
        self.audio = MyAudio(...)
        self.capture = MyCapture(...)

        self.initialized = True

    def stop(self):
        if not self.initialized:
            return

        # Release native resources.

        self.initialized = False
```

Again, the class does not have to inherit from `Backend`. It simply needs to satisfy the protocol.

---

## Step 4: Create a builder

```python
class MyBackendBuilder(BackendBuilder):
    def build(
        self,
        config: dict[str, Any],
    ) -> Backend:
        backend_config = (
            MyBackendConfig.from_dict(config)
        )

        return MyBackend(
            backend_config
        )
```

---

## Step 5: Register the backend

Built-in Tatuy backends are registered using:

```python
@BackendRegistry.implementation(
    "mybackend"
)
class MyBackendBuilder(BackendBuilder):
    ...
```

When using the built-in package convention, Tatuy expects the registration to live in:

```text
tatuy.backend.mybackend.builder
```

That allows `BackendFactory` to discover it lazily.

After registration:

```python
backend = BackendFactory.create(
    "mybackend",
    config,
)
```

works like any other backend.

---

## Backend Design Guidelines

When implementing or extending a backend, try to preserve these rules.

### Do not leak backend-specific types

Prefer:

```python
Key.SPACE
```

over:

```python
pygame.K_SPACE
```

Prefer:

```python
Vec2
```

over a backend-specific vector class.

Prefer Tatuy events over native events.

Once a Pygame type crosses the backend boundary, the abstraction has sprung a leak: One leak becomes three, three become twelve, then somebody says:

> "Maybe we should just import pygame here."

And that's how the Sith win.

---

### Keep capabilities focused

If code renders things, it probably belongs in the renderer. If it controls the operating system window, it probably belongs in the window capability. If it reads input state, it probably belongs in input.

Avoid adding convenience methods to `Backend` just because it is easy. The backend should compose capabilities, not slowly absorb them.

---

### Depend on the smallest interface

If something needs `Renderer`, give it a `Renderer`, if it only needs `Text`, give it `Text`. Do not pass the entire backend everywhere, this keeps dependencies visible and makes replacing implementations significantly easier.

---

### Backend implementations may be ugly

This is actually allowed. Platform code is often messy: There will be Pygame quirks, there will eventually be SDL pointers, there may be native handles, there will definitely be comments explaining why removing one suspicious line causes Windows to summon a segmentation fault. All of that is fine. The purpose of the backend boundary is not to eliminate platform-specific ugliness, it is to **contain it**. The rest of Tatuy should not care.

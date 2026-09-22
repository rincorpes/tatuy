
# Backend Architecture

One of the original ideas behind Tatuy was simple:

> Write games in Python, then move performance-sensitive parts somewhere faster when they actually become a problem.

Not when Reddit says they might become a problem, not because somebody on Hacker News benchmarked a for-loop, bu when they **actually** become a problem. To make that possible, the engine itself needs to be backend agnostic.

Tatuy should not care whether a rectangle is eventually rendered by Pygame, SDL2, OpenGL, Vulkan, an ancient ritual involving assembly, or something I have not regretted implementing yet.

There are a few architectural rules that make this possible.

## 1. Tatuy depends on protocols, not implementations

Code inside the engine should not depend on a concrete backend.

Instead of:

```python
def run(backend: PygameBackend):
    ...
```

Tatuy depends on:

```python
def run(backend: Backend):
    ...
```

The `Backend` protocol defines what Tatuy expects:

```python
class Backend(Protocol):
    @property
    def config(self) -> BackendConfig: ...

    @property
    def events(self) -> Events: ...

    @property
    def window(self) -> Window: ...

    @property
    def audio(self) -> Audio: ...

    @property
    def capture(self) -> Capture: ...

    @property
    def input(self) -> Input: ...

    @property
    def renderer(self) -> Renderer: ...

    viewport_transform: ViewportTransform
    initialized: bool

    def init(self) -> None: ...
    def stop(self) -> None: ...
```

This means the rest of the engine knows what a backend **can do**, but does not need to know **how it does it**.

Pygame can use `pygame.draw.rect`. A future SDL backend can use `SDL_RenderFillRect`, Tatuy does not care, Tatuy has enough problems already.

---

## 2. Backends expose capabilities

The backend itself is not intended to become a giant god object containing every platform-related function known to humanity.

That road starts with:

```python
backend.draw_rect(...)
```

and six months later ends with:

```python
backend.do_everything(True)
```

Instead, the backend acts as a composition root for a set of focused capabilities.

So instead of:

```python
backend.draw_rect(...)
backend.play_sound(...)
backend.set_cursor(...)
backend.capture(...)
```

we use:

```python
backend.renderer.shape.rect(...)
backend.audio.play_sound(...)
backend.input.set_cursor(...)
backend.capture.bmp(...)
```

Each capability owns a specific area of responsibility.

```text
Backend
├── Window
├── Events
├── Input
├── Renderer
├── Audio
└── Capture
```

Rendering is further divided into smaller capabilities:

```text
Renderer
├── Shape
├── Text
├── Texture
└── Clip
```

This gives the backend a clear structure and prevents unrelated platform functionality from becoming coupled together.

---

## 3. Capabilities can be depended on individually

Not every part of Tatuy needs the entire backend.

A rendering system only needs a renderer, an audio service only needs audio, a UI component may only need text rendering.

So this:

```python
class RenderSystem:
    def __init__(self, renderer: Renderer):
        self.renderer = renderer
```

is preferred over:

```python
class RenderSystem:
    def __init__(self, backend: Backend):
        self.backend = backend
```

The general rule is:

> Depend on the smallest capability you actually need.

This keeps dependencies explicit and makes systems easier to test, replace, and understand.

It also prevents the classic:

```python
self.backend.window.renderer.audio.input.something
```

situation where nobody remembers why the class received the backend in the first place.

# Backend Examples

These examples explore Tatuy's lowest platform-facing layer: the backend.

A backend is responsible for communicating with things Tatuy would rather not marry directly:

* windows,
* operating-system events,
* keyboards and mice,
* rendering,
* audio,
* frame capture,
* and whichever platform API Future Me decides was a great idea to support.

The examples in this section intentionally work **directly with the backend**.

You will not see scenes, ECS systems, `InputFrame`, runtime services, or gameplay here.

Those systems consume information produced by the backend, but they belong to higher layers of Tatuy.

The progression is:

```text
Backend
   ↓
Window / Events / Input
   ↓
Rendering / Audio / Capture
   ↓
Engine services
   ↓
Scenes / ECS / Gameplay
```

This section stops before the engine-services part.

---

## Backend

[`examples/fundamentals/001_backend/app.py`](../../examples/fundamentals/001_backend/app.py)

This is the smallest possible backend example.

It shows the basic lifecycle:

```text
configure
   ↓
construct
   ↓
initialize
   ↓
use
   ↓
stop
```

```python
from __future__ import annotations

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)


def main():
    config = PygameBackendConfig()

    backend = PygameBackend(
        config=config,
    )

    backend.init()

    print(backend)

    backend.stop()


if __name__ == "__main__":
    main()
```

### 1. Backend configuration

Every backend receives a configuration object.

```python
config = PygameBackendConfig()
```

`PygameBackendConfig` provides defaults, so nothing needs to be configured for this example.

### 2. Backend construction

```python
backend = PygameBackend(
    config=config,
)
```

Construction stores configuration and creates backend-level state such as the viewport transform.

Platform components are not created until `init()` is called.

Creating a Python object should not suddenly open a window and awaken the audio driver from its eternal slumber.

### 3. Initialization

```python
backend.init()
```

For Pygame this initializes Pygame itself and creates the concrete backend components:

```text
Events
Window
Input
Renderer
Audio
Capture
```

The window is created as a backend component, but the actual operating-system window is still opened explicitly through:

```python
backend.window.open()
```

### 4. Shutdown

```python
backend.stop()
```

`stop()` releases Pygame resources and marks the backend as no longer initialized.

---

## Basic Configuration

[`001_basic_config/app.py`](../../examples/fundamentals/001_backend/001_basic_config/app.py)

A backend can be configured by composing its configuration dataclasses.

```python
from __future__ import annotations

import json

from tatuy.backend.config import (
    FontConfig,
    SoundConfig,
    TextConfig,
)
from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)
from tatuy.backend.pygame.config import (
    PygameAudioConfig,
    PygameCaptureConfig,
    PygameEventsConfig,
    PygameInputConfig,
    PygameRendererConfig,
    PygameWindowConfig,
)


def main():
    config = PygameBackendConfig(
        window=PygameWindowConfig(
            width=1200,
            height=720,
            title="My Game",
            resizable=True,
        ),
        events=PygameEventsConfig(),
        input=PygameInputConfig(),
        renderer=PygameRendererConfig(
            background_color=(20, 20, 20),
            text=TextConfig(
                fonts=(
                    FontConfig(
                        name="ui",
                        path="assets/fonts/ui.ttf",
                    ),
                ),
                default_font="ui",
            ),
        ),
        audio=PygameAudioConfig(
            enabled=False,
            master_volume=0.5,
            frequency=44100,
            channels=2,
            chunk_size=2048,
            sounds=(),
        ),
        capture=PygameCaptureConfig(),
    )

    backend = PygameBackend(config)

    backend.init()

    print(
        json.dumps(
            backend.config.to_dict(),
            indent=2,
        )
    )

    backend.stop()


if __name__ == "__main__":
    main()
```

The configuration tree mirrors the backend capability tree:

```text
BackendConfig
├── events
├── window
├── input
├── renderer
│   └── text
├── audio
└── capture
```

Not every configuration option is implemented yet.

In particular, the input enable/disable flags currently exist as part of the intended API but do not yet change Pygame behavior.

They are configuration, not magic. Yet.

---

## Dictionary Configuration

[`002_dict_config/app.py`](../../examples/fundamentals/001_backend/002_dict_config/app.py)

Backend configuration can also be built from a dictionary.

```python
from __future__ import annotations

import json

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)


def main():
    config_data = {
        "window": {
            "width": 1200,
            "height": 720,
            "title": "My Game",
            "resizable": True,
        },
        "renderer": {
            "background_color": (
                20,
                20,
                20,
            ),
        },
        "audio": {
            "enabled": False,
            "master_volume": 0.5,
        },
    }

    config = PygameBackendConfig.from_dict(
        config_data
    )

    backend = PygameBackend(config)
    backend.init()

    print(
        json.dumps(
            backend.config.to_dict(),
            indent=2,
        )
    )

    backend.stop()


if __name__ == "__main__":
    main()
```

`from_dict()` recursively converts nested dictionaries into their corresponding configuration dataclasses.

This is important because Tatuy project configuration will usually come from external data rather than someone lovingly hand-writing seven nested dataclasses every morning.

Conceptually:

```text
dictionary
    ↓
PygameBackendConfig.from_dict()
    ↓
PygameBackendConfig
    ├── PygameWindowConfig
    ├── PygameRendererConfig
    └── ...
```

---

## Backend Factory

[`003_factory/app.py`](../../examples/fundamentals/001_backend/003_factory/app.py)

So far we have instantiated `PygameBackend` directly.

Tatuy also provides a backend factory.

This is the normal route when the selected backend comes from application configuration.

```python
from __future__ import annotations

from tatuy.backend.factory import BackendFactory


def main():
    config = {
        "window": {
            "width": 1280,
            "height": 720,
            "title": "Factory Example",
        },
    }

    backend = BackendFactory.create(
        "pygame",
        config,
    )

    backend.init()

    print(backend)

    backend.stop()


if __name__ == "__main__":
    main()
```

The factory turns:

```text
backend name
     +
configuration
     ↓
BackendFactory
     ↓
BackendBuilder
     ↓
Concrete Backend
```

into a backend instance.

This means application code does not need:

```python
if backend_name == "pygame":
    ...
elif backend_name == "sdl":
    ...
elif backend_name == "i-have-made-poor-life-choices":
    ...
```

---

## Window

[`004_window/app.py`](../../examples/fundamentals/001_backend/004_window/app.py)

The `Window` capability controls the native game window.

```python
from __future__ import annotations

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)


def main():
    config = PygameBackendConfig.from_dict(
        {
            "window": {
                "width": 1280,
                "height": 720,
                "title": "Window Example",
                "resizable": True,
            }
        }
    )

    backend = PygameBackend(config)
    backend.init()

    backend.window.open()

    print(
        "Window size:",
        backend.window.size,
    )

    backend.window.set_title(
        "Tatuy Window"
    )

    print("Press CTRL+C to exit")

    try:
        while True:
            # Poll events so the OS does not
            # consider the application dead.
            backend.events.get_events()

    except KeyboardInterrupt:
        pass

    finally:
        backend.stop()


if __name__ == "__main__":
    main()
```

Initializing a backend does not automatically open the native window.

```python
backend.window.open()
```

does that explicitly.

The window capability also exposes operations such as:

```python
backend.window.size
backend.window.set_title(...)
backend.window.resize(...)
```

---

## Events

[`005_events/app.py`](../../examples/fundamentals/001_backend/005_events/app.py)

The event capability is responsible for retrieving **native platform events and translating them into Tatuy events**.

This example deliberately does not use Tatuy's event bus.

We want to see exactly what comes out of the backend boundary.

```python
from __future__ import annotations

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)
from tatuy.events import EventType


def main():
    backend = PygameBackend(
        PygameBackendConfig()
    )

    backend.init()
    backend.window.open()

    running = True

    try:
        while running:
            events = (
                backend.events.get_events()
            )

            for event in events:
                print(
                    event.type,
                    event.attrs,
                )

                if event.type == EventType.QUIT:
                    running = False

    finally:
        backend.stop()


if __name__ == "__main__":
    main()
```

Pygame produces things such as:

```text
pygame.KEYDOWN
pygame.MOUSEMOTION
pygame.WINDOWRESIZED
```

The backend converts those into Tatuy concepts before returning them:

```text
Pygame event
     ↓
PygameEvents
     ↓
Tatuy Event
```

For example, a Pygame keyboard code becomes a Tatuy `Key`.

Anything above this layer should not need to know what `pygame.K_SPACE` is.

That knowledge stays in containment where it belongs.

---

## Input

[`006_input/app.py`](../../examples/fundamentals/001_backend/006_input/app.py)

Events describe things that happened.

The input capability can also expose the **current state** of an input device.

The current backend API provides pointer state and cursor control.

```python
from __future__ import annotations

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)
from tatuy.events import EventType
from tatuy.input.pointer import Cursor


def main():
    backend = PygameBackend(
        PygameBackendConfig()
    )

    backend.init()
    backend.window.open()

    backend.input.set_cursor(
        Cursor.HAND
    )

    running = True

    try:
        while running:
            for event in backend.events.get_events():
                if event.type == EventType.QUIT:
                    running = False

            pointer = (
                backend.input.get_pointer_state()
            )

            print(pointer)

    finally:
        backend.stop()


if __name__ == "__main__":
    main()
```

The distinction is important:

```text
Events
    ↓
"Something happened."

Input state
    ↓
"What is true right now?"
```

Higher-level systems such as `InputService` can combine both forms of information later to build an `InputFrame`.

That happens above the backend layer.

---

## Renderer

[`007_renderer/app.py`](../../examples/fundamentals/001_backend/007_renderer/app.py)

The renderer controls frame presentation.

Its most basic lifecycle is:

```text
begin_frame()
    ↓
draw
    ↓
end_frame()
```

```python
from __future__ import annotations

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)
from tatuy.events import EventType


def main():
    backend = PygameBackend(
        PygameBackendConfig()
    )

    backend.init()
    backend.window.open()

    backend.renderer.set_clear_color(
        30,
        30,
        30,
    )

    running = True

    try:
        while running:
            for event in backend.events.get_events():
                if event.type == EventType.QUIT:
                    running = False

            backend.renderer.begin_frame()

            # Draw commands go here.

            backend.renderer.end_frame()

    finally:
        backend.stop()


if __name__ == "__main__":
    main()
```

`begin_frame()` prepares a new frame and clears the previous one.

`end_frame()` presents the completed frame.

Anything drawn between them belongs to the current frame.

---

### Shapes

[`007_renderer/001_shapes/app.py`](../../examples/fundamentals/001_backend/007_renderer/001_shapes/app.py)

Primitive shapes are available through:

```python
backend.renderer.shape
```

```python
from __future__ import annotations

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)
from tatuy.events import EventType
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


def main():
    backend = PygameBackend(
        PygameBackendConfig()
    )

    backend.init()
    backend.window.open()

    running = True

    try:
        while running:
            for event in backend.events.get_events():
                if event.type == EventType.QUIT:
                    running = False

            backend.renderer.begin_frame()

            backend.renderer.shape.rect(
                pos=Vec2(40, 40),
                size=Size(160, 80),
                color=(220, 80, 80),
                radius=10,
            )

            backend.renderer.shape.line(
                start=Vec2(40, 160),
                end=Vec2(300, 160),
                color=(255, 255, 255),
                thickness=4,
            )

            backend.renderer.shape.circle(
                400,
                180,
                radius=50,
                color=(80, 180, 255),
            )

            backend.renderer.shape.polygon(
                [
                    (500, 100),
                    (580, 180),
                    (460, 220),
                ],
                color=(180, 255, 100),
            )

            backend.renderer.end_frame()

    finally:
        backend.stop()


if __name__ == "__main__":
    main()
```

The current shape implementation supports:

```text
Rectangle
Line
Circle
Polygon
```

Shapes are described using Tatuy types and logical coordinates.

The backend is responsible for translating those instructions into the actual rendering library.

---

### Text

[`007_renderer/002_text/app.py`](../../examples/fundamentals/001_backend/007_renderer/002_text/app.py)

Text rendering lives under:

```python
backend.renderer.text
```

```python
from __future__ import annotations

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)
from tatuy.events import EventType


def main():
    backend = PygameBackend(
        PygameBackendConfig()
    )

    backend.init()
    backend.window.open()

    running = True

    try:
        while running:
            for event in backend.events.get_events():
                if event.type == EventType.QUIT:
                    running = False

            width, height = (
                backend.renderer.text.measure(
                    "Hello Tatuy",
                    font_size=32,
                )
            )

            backend.renderer.begin_frame()

            backend.renderer.text.draw(
                x=40,
                y=40,
                text="Hello Tatuy",
                color=(255, 255, 255),
                font_size=32,
            )

            backend.renderer.text.draw(
                x=40,
                y=100,
                text=f"{width} x {height}",
                color=(160, 160, 160),
                font_size=20,
            )

            backend.renderer.end_frame()

    finally:
        backend.stop()


if __name__ == "__main__":
    main()
```

`measure()` returns the logical width and height of rendered text.

That becomes useful for things such as:

```text
centering
UI layout
buttons
menus
HUDs
```

because text apparently needed geometry too.

---

### Textures

[`007_renderer/003_textures/app.py`](../../examples/fundamentals/001_backend/007_renderer/003_textures/app.py)

Textures are backend-managed images.

The backend receives RGBA pixel data and returns an integer texture handle.

For a self-contained example we can generate a tiny checkerboard instead of depending on an asset file.

```python
from __future__ import annotations

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)
from tatuy.events import EventType


def create_checkerboard(
    width: int,
    height: int,
) -> bytes:
    data = bytearray()

    for y in range(height):
        for x in range(width):
            bright = (
                (x // 8) + (y // 8)
            ) % 2 == 0

            value = 255 if bright else 40

            data.extend(
                (
                    value,
                    value,
                    value,
                    255,
                )
            )

    return bytes(data)


def main():
    backend = PygameBackend(
        PygameBackendConfig()
    )

    backend.init()
    backend.window.open()

    pixels = create_checkerboard(
        64,
        64,
    )

    texture = (
        backend.renderer.texture.create(
            64,
            64,
            pixels,
        )
    )

    running = True

    try:
        while running:
            for event in backend.events.get_events():
                if event.type == EventType.QUIT:
                    running = False

            backend.renderer.begin_frame()

            backend.renderer.texture.draw(
                texture,
                x=100,
                y=100,
                w=128,
                h=128,
            )

            backend.renderer.texture.draw(
                texture,
                x=300,
                y=100,
                w=128,
                h=128,
                angle_deg=45,
            )

            backend.renderer.end_frame()

    finally:
        backend.renderer.texture.destroy(
            texture
        )
        backend.stop()


if __name__ == "__main__":
    main()
```

Game code receives a backend-neutral integer handle rather than a Pygame `Surface`.

A different backend may store a completely different native texture representation.

Tatuy remains blissfully unaware.

---

### Clipping

[`007_renderer/004_clipping/app.py`](../../examples/fundamentals/001_backend/007_renderer/004_clipping/app.py)

Clipping restricts rendering to a rectangular area.

```python
from __future__ import annotations

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)
from tatuy.events import EventType
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


def main():
    backend = PygameBackend(
        PygameBackendConfig()
    )

    backend.init()
    backend.window.open()

    running = True

    try:
        while running:
            for event in backend.events.get_events():
                if event.type == EventType.QUIT:
                    running = False

            backend.renderer.begin_frame()

            backend.renderer.clip.set(
                pos=Vec2(100, 100),
                size=Size(200, 150),
            )

            backend.renderer.shape.rect(
                pos=Vec2(50, 50),
                size=Size(400, 300),
                color=(100, 180, 255),
            )

            backend.renderer.clip.clear()

            backend.renderer.end_frame()

    finally:
        backend.stop()


if __name__ == "__main__":
    main()
```

Although the rectangle is larger than the clipping region, only the area inside the clip is rendered.

This becomes useful for things such as scroll views, panels, editors, and UI containers.

---

### Viewport Transform

[`007_renderer/005_viewport/app.py`](../../examples/fundamentals/001_backend/007_renderer/005_viewport/app.py)

Render commands operate in logical Tatuy coordinates.

`ViewportTransform` maps those coordinates into actual display coordinates.

The transform contains:

```text
ox   horizontal offset
oy   vertical offset
s    scale
```

```python
from __future__ import annotations

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)
from tatuy.events import EventType
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


def main():
    backend = PygameBackend(
        PygameBackendConfig()
    )

    backend.init()
    backend.window.open()

    backend.viewport_transform.set(
        offset_x=200,
        offset_y=100,
        scale=2.0,
    )

    running = True

    try:
        while running:
            for event in backend.events.get_events():
                if event.type == EventType.QUIT:
                    running = False

            backend.renderer.begin_frame()

            backend.renderer.shape.rect(
                pos=Vec2(20, 20),
                size=Size(100, 50),
                color=(255, 120, 80),
            )

            backend.renderer.end_frame()

    finally:
        backend.viewport_transform.clear()
        backend.stop()


if __name__ == "__main__":
    main()
```

The game asks to draw at:

```text
20, 20
```

but the renderer applies the viewport transform before the backend draws it.

Conceptually:

```text
logical coordinates
       ↓
ViewportTransform
       ↓
display coordinates
```

This is what will eventually allow logical resolutions, scaling, letterboxing, cameras, and similar systems to exist without every drawing call having an existential crisis.

---

## Audio

[`008_audio/app.py`](../../examples/fundamentals/001_backend/008_audio/app.py)

Audio is disabled by default.

It can be enabled and initialized manually.

```python
from __future__ import annotations

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)
from tatuy.backend.pygame.config import (
    PygameAudioConfig,
)


def main():
    config = PygameBackendConfig(
        audio=PygameAudioConfig(
            enabled=True,
            auto_init=False,
        )
    )

    backend = PygameBackend(config)

    backend.init()

    # Because auto_init=False.
    backend.audio.init()

    backend.audio.load_sound(
        "test",
        "assets/audio/test.wav",
    )

    backend.audio.play_sound(
        "test"
    )

    input(
        "Press ENTER to stop..."
    )

    backend.audio.stop_all()
    backend.audio.shutdown()
    backend.stop()


if __name__ == "__main__":
    main()
```

Using:

```python
auto_init=False
```

means backend initialization creates the audio component but does not initialize Pygame's mixer automatically.

This is useful when audio resources need to be prepared manually.

---

### Audio Autoload

[`001_backend/014_audio/001_autoload/app.py`](../../examples/fundamentals/001_backend/014_audio/001_autoload/app.py)

Sounds can also be declared in configuration.

```python
from __future__ import annotations

from tatuy.backend.config import SoundConfig
from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)
from tatuy.backend.pygame.config import (
    PygameAudioConfig,
)


def main():
    config = PygameBackendConfig(
        audio=PygameAudioConfig(
            enabled=True,
            auto_init=True,
            master_volume=0.5,
            sounds=(
                SoundConfig(
                    name="test",
                    path="assets/audio/test.wav",
                ),
            ),
        )
    )

    backend = PygameBackend(config)

    backend.init()

    backend.audio.play_sound(
        "test"
    )

    input(
        "Press ENTER to stop..."
    )

    backend.stop()


if __name__ == "__main__":
    main()
```

When both:

```python
enabled=True
auto_init=True
```

are configured, backend initialization initializes audio and loads configured sounds.

---

## Capture

[`009_capture/app.py`](../../examples/fundamentals/001_backend/009_capture/app.py)

The capture capability can save the current contents of the game window.

```python
from __future__ import annotations

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


def main():
    backend = PygameBackend(
        PygameBackendConfig()
    )

    backend.init()
    backend.window.open()

    backend.renderer.begin_frame()

    backend.renderer.shape.rect(
        pos=Vec2(100, 100),
        size=Size(300, 200),
        color=(100, 180, 255),
    )

    backend.renderer.end_frame()

    backend.capture.bmp(
        "capture.bmp"
    )

    backend.stop()


if __name__ == "__main__":
    main()
```

The current API receives the output path directly.

Although `CaptureConfig` already contains fields such as `directory` and `format`, those values are not currently used by `PygameCapture.bmp()`.

The configuration exists ahead of the final capture workflow.

---

### Raw Frame Capture

[`009_capture/001_raw/app.py`](../../examples/fundamentals/001_backend/009_capture/001_raw/app.py)

The capture capability can also return the raw framebuffer.

```python
from __future__ import annotations

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)


def main():
    backend = PygameBackend(
        PygameBackendConfig()
    )

    backend.init()
    backend.window.open()

    backend.renderer.begin_frame()
    backend.renderer.end_frame()

    width, height, data = (
        backend.capture.bgra8888_bytes()
    )

    print(
        "width:",
        width,
    )
    print(
        "height:",
        height,
    )
    print(
        "bytes:",
        len(data),
    )

    backend.stop()


if __name__ == "__main__":
    main()
```

This API exists primarily for lower-level systems such as:

```text
frame recording
video capture
streaming
image processing
```

Normal gameplay code should generally not need raw framebuffer bytes.

If Pong starts manually inspecting BGRA buffers, something has gone terribly wrong.

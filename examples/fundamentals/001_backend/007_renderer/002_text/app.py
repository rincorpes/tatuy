from __future__ import annotations

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)
from tatuy.events import EventType


def main():
    backend = PygameBackend(PygameBackendConfig())

    backend.init()
    backend.window.open()

    running = True

    try:
        while running:
            for event in backend.events.get_events():
                if event.type == EventType.QUIT:
                    running = False

            width, height = backend.renderer.text.measure(
                "Hello Tatuy",
                font_size=32,
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

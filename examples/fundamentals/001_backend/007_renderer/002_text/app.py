from __future__ import annotations

from tatuy.backend.config import FontConfig, TextConfig
from tatuy.backend.pygame import PygameBackend, PygameBackendConfig
from tatuy.backend.pygame.config import PygameRendererConfig
from tatuy.events import EventType


def main():
    backend = PygameBackend(
        PygameBackendConfig(
            renderer=PygameRendererConfig(
                text=TextConfig(
                    fonts=(FontConfig(name="ui", size=32),), default_font="ui"
                )
            )
        )
    )
    try:
        backend.init()
        backend.window.open()
        running = True
        while running:
            for event in backend.events.get_events():
                if event.type == EventType.QUIT:
                    running = False
            width, height = backend.renderer.text.measure(
                "Hello Tatuy",
            )
            backend.renderer.begin_frame()
            backend.renderer.text.draw(
                x=40,
                y=40,
                text="Hello Tatuy",
                color=(255, 255, 255),
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

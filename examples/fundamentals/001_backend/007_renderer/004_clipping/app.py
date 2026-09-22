from __future__ import annotations

from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)
from tatuy.events import EventType
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2


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

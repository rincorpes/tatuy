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

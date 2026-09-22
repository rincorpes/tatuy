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

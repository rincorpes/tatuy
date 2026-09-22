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
            bright = ((x // 8) + (y // 8)) % 2 == 0

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
    backend = PygameBackend(PygameBackendConfig())

    backend.init()
    backend.window.open()

    pixels = create_checkerboard(
        64,
        64,
    )

    texture = backend.renderer.texture.create(
        64,
        64,
        pixels,
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
        backend.renderer.texture.destroy(texture)
        backend.stop()


if __name__ == "__main__":
    main()

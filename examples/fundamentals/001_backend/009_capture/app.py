from __future__ import annotations

import os

from tatuy.backend.pygame import PygameBackend, PygameBackendConfig
from tatuy.geometry.size import Size
from tatuy.math.vec2 import Vec2

ROOT = ".tatuy"


def main():
    backend = PygameBackend(PygameBackendConfig())

    backend.init()
    backend.window.open()

    backend.renderer.begin_frame()

    backend.renderer.shape.rect(
        pos=Vec2(100, 100),
        size=Size(300, 200),
        color=(100, 180, 255),
    )

    backend.renderer.end_frame()

    os.makedirs(ROOT, exist_ok=True)

    path = f"{ROOT}/capture.bmp"

    backend.capture.bmp(path)

    backend.stop()

    print("See the image: ", path)


if __name__ == "__main__":
    main()

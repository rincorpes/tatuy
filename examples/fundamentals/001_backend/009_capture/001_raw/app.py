from __future__ import annotations

from tatuy.backend.pygame import PygameBackend, PygameBackendConfig


def main():
    backend = PygameBackend(PygameBackendConfig())
    try:
        backend.init()
        backend.window.open()
        backend.renderer.begin_frame()
        backend.renderer.end_frame()
        width, height, data = backend.capture.bgra8888_bytes()
        print("width:", width)
        print("height:", height)
        print("bytes:", len(data))
    finally:
        backend.stop()


if __name__ == "__main__":
    main()

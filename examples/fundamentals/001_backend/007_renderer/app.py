from __future__ import annotations

from tatuy.backend.pygame import PygameBackend, PygameBackendConfig
from tatuy.events import EventType


def main():
    backend = PygameBackend(PygameBackendConfig())
    try:
        backend.init()
        backend.window.open()
        backend.renderer.set_clear_color(30, 30, 30)
        running = True
        while running:
            for event in backend.events.get_events():
                if event.type == EventType.QUIT:
                    running = False
            backend.renderer.begin_frame()
            backend.renderer.end_frame()
    finally:
        backend.stop()


if __name__ == "__main__":
    main()

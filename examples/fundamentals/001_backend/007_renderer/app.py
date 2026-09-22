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

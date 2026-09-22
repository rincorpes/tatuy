from __future__ import annotations

from tatuy.backend.pygame import PygameBackend, PygameBackendConfig
from tatuy.events import EventType


def main():
    backend = PygameBackend(PygameBackendConfig())

    backend.init()
    backend.window.open()

    running = True

    try:
        while running:
            events = backend.events.get_events()

            for event in events:
                print(
                    event.type,
                    event.attrs,
                )

                if event.type == EventType.QUIT:
                    running = False

    finally:
        backend.stop()


if __name__ == "__main__":
    main()

from __future__ import annotations

from tatuy.backend.pygame import PygameBackend, PygameBackendConfig
from tatuy.events import EventType
from tatuy.input.pointer import Cursor


def main():
    backend = PygameBackend(PygameBackendConfig())

    backend.init()
    backend.window.open()

    backend.input.set_cursor(Cursor.HAND)

    running = True

    try:
        while running:
            for event in backend.events.get_events():
                if event.type == EventType.QUIT:
                    running = False

            pointer = backend.input.get_pointer_state()

            print(pointer)

    finally:
        backend.stop()


if __name__ == "__main__":
    main()

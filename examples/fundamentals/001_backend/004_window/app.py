from __future__ import annotations

from tatuy.backend.pygame import PygameBackend, PygameBackendConfig
from tatuy.events import EventType


def main():
    config = PygameBackendConfig.from_dict(
        {
            "window": {
                "width": 1280,
                "height": 720,
                "title": "Window Example",
                "resizable": True,
            }
        }
    )
    backend = PygameBackend(config)
    try:
        backend.init()
        backend.window.open()
        print("Window size:", backend.window.size)
        backend.window.set_title("Tatuy Window")
        print("Close the window or press CTRL+C to exit")
        try:
            while True:
                if any(
                    (
                        event.type in (EventType.QUIT, EventType.WINDOWCLOSE)
                        for event in backend.events.get_events()
                    )
                ):
                    break
        except KeyboardInterrupt:
            pass
    finally:
        backend.stop()


if __name__ == "__main__":
    main()

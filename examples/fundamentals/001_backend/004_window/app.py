from __future__ import annotations

from tatuy.backend.pygame import PygameBackend, PygameBackendConfig


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
    backend.init()

    backend.window.open()

    print(
        "Window size:",
        backend.window.size,
    )

    backend.window.set_title("Tatuy Window")

    print("Press CTRL+C to exit")

    try:
        while True:
            # Poll events so the OS does not
            # consider the application dead.
            backend.events.get_events()

    except KeyboardInterrupt:
        pass

    finally:
        backend.stop()


if __name__ == "__main__":
    main()

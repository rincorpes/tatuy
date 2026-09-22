from __future__ import annotations

from tatuy.backend.factory import BackendFactory


def main():
    config = {
        "window": {
            "width": 1280,
            "height": 720,
            "title": "Factory Example",
        },
    }

    backend = BackendFactory.create(
        "pygame",
        config,
    )

    backend.init()

    print(backend)

    backend.stop()


if __name__ == "__main__":
    main()

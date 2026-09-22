from __future__ import annotations

from tatuy.backend.pygame import PygameBackend, PygameBackendConfig


def main():
    config = PygameBackendConfig()

    backend = PygameBackend(
        config=config,
    )

    backend.init()

    print(backend)

    backend.stop()


if __name__ == "__main__":
    main()

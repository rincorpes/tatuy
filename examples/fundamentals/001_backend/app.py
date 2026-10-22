from __future__ import annotations

from tatuy.backend.pygame import PygameBackend, PygameBackendConfig


def main():
    config = PygameBackendConfig()

    backend = PygameBackend(
        config=config,
    )

    try:
        backend.init()
        print(backend)
    finally:
        backend.stop()


if __name__ == "__main__":
    main()

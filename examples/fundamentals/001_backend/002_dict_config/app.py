from __future__ import annotations

import json

from tatuy.backend.pygame import PygameBackend, PygameBackendConfig


def main():
    config_data = {
        "window": {
            "width": 1200,
            "height": 720,
            "title": "My Game",
            "resizable": True,
        },
        "renderer": {
            "background_color": (
                20,
                20,
                20,
            ),
        },
        "audio": {
            "enabled": False,
            "master_volume": 0.5,
        },
    }

    config = PygameBackendConfig.from_dict(config_data)

    backend = PygameBackend(config)
    backend.init()

    print(
        json.dumps(
            backend.config.to_dict(),
            indent=2,
        )
    )

    backend.stop()


if __name__ == "__main__":
    main()

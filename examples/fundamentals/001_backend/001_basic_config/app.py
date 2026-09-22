from __future__ import annotations

import json

from tatuy.backend.config import FontConfig, TextConfig
from tatuy.backend.pygame import PygameBackend, PygameBackendConfig
from tatuy.backend.pygame.config import (
    PygameAudioConfig,
    PygameCaptureConfig,
    PygameEventsConfig,
    PygameInputConfig,
    PygameRendererConfig,
    PygameWindowConfig,
)


def main():
    config = PygameBackendConfig(
        window=PygameWindowConfig(
            width=1200,
            height=720,
            title="My Game",
            resizable=True,
        ),
        events=PygameEventsConfig(),
        input=PygameInputConfig(),
        renderer=PygameRendererConfig(
            background_color=(20, 20, 20),
            text=TextConfig(
                fonts=(
                    FontConfig(
                        name="ui",
                        path="assets/fonts/ui.ttf",
                    ),
                ),
                default_font="ui",
            ),
        ),
        audio=PygameAudioConfig(
            enabled=False,
            master_volume=0.5,
            frequency=44100,
            channels=2,
            chunk_size=2048,
            sounds=(),
        ),
        capture=PygameCaptureConfig(),
    )

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

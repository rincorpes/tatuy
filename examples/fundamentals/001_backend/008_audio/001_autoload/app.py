from __future__ import annotations

from tatuy.backend.config import SoundConfig
from tatuy.backend.pygame import (
    PygameBackend,
    PygameBackendConfig,
)
from tatuy.backend.pygame.config import (
    PygameAudioConfig,
)


def main():
    config = PygameBackendConfig(
        audio=PygameAudioConfig(
            enabled=True,
            auto_init=True,
            master_volume=0.5,
            sounds=(
                SoundConfig(
                    name="test",
                    path="./examples/fundamentals/001_backend/008_audio/assets/test.wav",
                ),
            ),
        )
    )

    backend = PygameBackend(config)

    backend.init()

    backend.audio.play_sound("test")

    input("Press ENTER to stop...")

    backend.stop()


if __name__ == "__main__":
    main()

from __future__ import annotations

from tatuy.backend.pygame import PygameBackend, PygameBackendConfig
from tatuy.backend.pygame.config import PygameAudioConfig


def main():
    config = PygameBackendConfig(
        audio=PygameAudioConfig(
            enabled=True,
            auto_init=False,
        )
    )

    backend = PygameBackend(config)

    backend.init()

    # Because auto_init=False.
    backend.audio.init()

    backend.audio.load_sound(
        "test",
        "./examples/fundamentals/001_backend/008_audio/assets/test.wav",
    )

    backend.audio.play_sound("test")

    input("Press ENTER to stop...")

    backend.audio.stop_all()
    backend.audio.shutdown()
    backend.stop()


if __name__ == "__main__":
    main()

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from tatuy.capture.settings import CaptureSettings


@dataclass
class CapturePathBuilder:
    directory: str | Path = "screenshots"
    prefix: str = "tatuy_"
    ext: str = "png"

    def build(self, label: str) -> Path:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        safe_label = "".join(
            (
                character
                if character.isalnum() or character in ("-", "_")
                else "_"
            )
            for character in label
        )

        name = f"{self.prefix}_{stamp}{safe_label}.{self.ext}"
        return Path(self.directory) / name


class CaptureDirectories:
    def __init__(self, settings: CaptureSettings) -> None:
        self.root = Path(settings.root_dir).expanduser().resolve()

        self.screenshots = self._resolve(settings.screenshots_dir)
        self.replays = self._resolve(settings.replays_dir)
        self.recordings = self._resolve(settings.recordings_dir)

    def _resolve(self, directory: str) -> Path:
        path = (self.root / directory).resolve()

        if not path.is_relative_to(self.root):
            raise ValueError(
                f"Capture directory {directory!r} " "must be inside root_dir"
            )

        return path

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tatuy.settings import SettingsBuilder, SettingsRegistry


@dataclass(frozen=True)
class ReplaySettings:
    enabled: bool = False
    filename: str = "session.jsonl"
    game_id: str = "tatuy"
    initial_scene: str = ""
    seed: int = 0


@SettingsRegistry.implementation("replay")
class ReplaySettingsBuilder(SettingsBuilder[ReplaySettings]):
    def build(self, config: dict[str, Any]) -> ReplaySettings:
        settings = ReplaySettings(**dict(config))

        if not settings.filename:
            raise ValueError("Replay filename cannot be empty")

        if not settings.game_id:
            raise ValueError("Replay game_id cannot be empty")

        return settings


@dataclass(frozen=True)
class CaptureSettings:
    hotkeys_enabled: bool = True

    root_dir: str = ".tatuy"

    screenshots_dir: str = "screenshots"
    replays_dir: str = "replays"
    recordings_dir: str = "recordings"

    ffmpeg_path: str = "ffmpeg"

    video_fps: int = 60
    capture_fps: int = 30

    video_codec: str = "libx264"
    video_crf: int = 18
    video_preset: str = "veryfast"

    keep_frames: bool = True
    worker_queue_size: int = 16


@SettingsRegistry.implementation("capture")
class CaptureSettingsBuilder(SettingsBuilder[CaptureSettings]):
    def build(self, config: dict[str, Any]) -> CaptureSettings:
        settings = CaptureSettings(**dict(config))

        if settings.video_fps <= 0:
            raise ValueError("video_fps must be positive")

        if settings.capture_fps <= 0:
            raise ValueError("capture_fps must be positive")

        if settings.worker_queue_size <= 0:
            raise ValueError("worker_queue_size must be positive")

        return settings

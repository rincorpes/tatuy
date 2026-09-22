from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class BaseJob:
    job_id: str


@dataclass(frozen=True)
class CaptureJob(BaseJob):
    out_path: Path

    bmp_path: Path | None = None

    w: int = 0
    h: int = 0
    pixels: bytes | None = None

    fmt: str = "BGRA"
    pitch: int | None = None

    target_size: tuple[int, int] | None = None


@dataclass(frozen=True)
class CaptureResult:
    job_id: str
    out_path: Path
    ok: bool
    error: str | None = None


@dataclass
class WorkerConfig:
    queue_size: int = 64
    on_done: Callable[[CaptureResult], None] | None = None

    name: str = "capture-worker"
    daemon: bool = True
    delete_temp: bool = False


@dataclass(frozen=True)
class ScreenshotRequest:
    job_id: str
    out_path: Path
    label: str

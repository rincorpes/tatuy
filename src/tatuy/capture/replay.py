from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from tatuy.capture.replay_format import ReplayReader, ReplayWriter
from tatuy.capture.replay_frame import ReplayFrame
from tatuy.capture.replay_header import ReplayHeader
from tatuy.input.frame import InputFrame


@dataclass(frozen=True)
class ReplayRecorderConfig:
    path: Path
    header: ReplayHeader


class ReplayRecorder:
    def __init__(self) -> None:
        self._writer: ReplayWriter | None = None
        self._index = 0

    @property
    def active(self) -> bool:
        return self._writer is not None

    @property
    def path(self) -> Path | None:
        return self._writer.path if self._writer is not None else None

    def start(self, config: ReplayRecorderConfig) -> None:
        if self.active:
            raise RuntimeError("ReplayRecorder is already active")

        writer = ReplayWriter(config.path, config.header)
        writer.open()

        self._writer = writer
        self._index = 0

    def record(self, input_frame: InputFrame, dt: float) -> None:
        if self._writer is None:
            return

        self._writer.write_frame(
            ReplayFrame(
                index=self._index,
                dt=dt,
                input_frame=input_frame,
            )
        )

        self._index += 1

    def stop(self) -> None:
        writer = self._writer
        self._writer = None

        if writer is not None:
            writer.close()


class ReplayPlayer:
    def __init__(self) -> None:
        self._reader: ReplayReader | None = None
        self._frames: Iterator[ReplayFrame] | None = None

    @property
    def active(self) -> bool:
        return self._frames is not None

    def start(self, path: Path) -> ReplayHeader:
        if self.active:
            raise RuntimeError("ReplayPlayer is already active")

        reader = ReplayReader(path)
        header = reader.open()

        self._reader = reader
        self._frames = reader.frames()

        return header

    def next(self) -> ReplayFrame | None:
        if self._frames is None:
            raise RuntimeError("ReplayPlayer is not active")

        try:
            return next(self._frames)
        except StopIteration:
            self.stop()
            return None
        except Exception:
            self.stop()
            raise

    def stop(self) -> None:
        reader = self._reader
        self._reader = None
        self._frames = None

        if reader is not None:
            reader.close()

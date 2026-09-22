from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Iterator, TextIO

from tatuy.capture.replay_frame import ReplayFrame
from tatuy.capture.replay_header import (
    REPLAY_MAGIC,
    REPLAY_VERSION,
    ReplayHeader,
)
from tatuy.input.frame import InputFrame


class ReplayWriter:
    def __init__(self, path: Path, header: ReplayHeader) -> None:
        self.path = path
        self.header = header
        self._file: TextIO | None = None

    def open(self) -> None:
        if self._file is not None:
            raise RuntimeError("ReplayWriter is already open")

        # Serialize before opening so invalid options do not truncate a file.
        payload = json.dumps(asdict(self.header), allow_nan=False)

        self.path.parent.mkdir(parents=True, exist_ok=True)
        stream = self.path.open("w", encoding="utf-8")

        try:
            stream.write(payload + "\n")
        except Exception:
            stream.close()
            raise

        self._file = stream

    def write_frame(self, frame: ReplayFrame) -> None:
        if self._file is None:
            raise RuntimeError("ReplayWriter is not open")

        if not math.isfinite(frame.dt) or frame.dt < 0:
            raise ValueError("Replay dt must be finite and nonnegative")

        payload = {
            "index": frame.index,
            "dt": frame.dt,
            "input": frame.input_frame.to_dict(),
        }

        self._file.write(json.dumps(payload, allow_nan=False) + "\n")

    def close(self) -> None:
        stream = self._file
        self._file = None

        if stream is not None:
            stream.close()


class ReplayReader:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._file: TextIO | None = None

    def open(self) -> ReplayHeader:
        if self._file is not None:
            raise RuntimeError("ReplayReader is already open")

        stream = self.path.open("r", encoding="utf-8")

        try:
            first_line = stream.readline()

            if not first_line:
                raise ValueError("Replay file is empty")

            header = ReplayHeader(**json.loads(first_line))

            if header.magic != REPLAY_MAGIC:
                raise ValueError("This is not a Tatuy replay")

            if header.version != REPLAY_VERSION:
                raise ValueError(
                    f"Unsupported replay version: {header.version}"
                )

            if header.fps <= 0:
                raise ValueError("Replay fps must be positive")

            if header.virtual_w <= 0 or header.virtual_h <= 0:
                raise ValueError("Replay dimensions must be positive")

            if header.initial_scene == "unknown":
                raise ValueError("Replay has no initial scene")

        except Exception:
            stream.close()
            raise

        self._file = stream
        return header

    def frames(self) -> Iterator[ReplayFrame]:
        if self._file is None:
            raise RuntimeError("ReplayReader is not open")

        expected_index = 0

        for line in self._file:
            if not line.strip():
                continue

            payload = json.loads(line)

            index = int(payload["index"])
            dt = float(payload["dt"])

            if index != expected_index:
                raise ValueError(
                    f"Expected replay frame {expected_index}, got {index}"
                )

            if not math.isfinite(dt) or dt < 0:
                raise ValueError("Invalid replay dt")

            yield ReplayFrame(
                index=index,
                dt=dt,
                input_frame=InputFrame.from_dict(payload["input"]),
            )

            expected_index += 1

    def close(self) -> None:
        stream = self._file
        self._file = None

        if stream is not None:
            stream.close()

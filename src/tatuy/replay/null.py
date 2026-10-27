"""Disabled replay capability for hosts without replay storage."""

from __future__ import annotations

from tatuy.capture.replay_frame import ReplayFrame
from tatuy.capture.replay_header import ReplayHeader
from tatuy.input.frame import InputFrame


class NullReplayService:
    """No-op replay implementation that preserves the runtime contract."""

    @property
    def enabled(self) -> bool:
        return False

    @property
    def recording(self) -> bool:
        return False

    @property
    def playing(self) -> bool:
        return False

    @property
    def header(self) -> ReplayHeader | None:
        return None

    def start_record(self, *, filename: str, header: ReplayHeader) -> None:
        del filename, header
        raise RuntimeError("Replay is disabled")

    def stop_record(self) -> None:
        return None

    def record_input(self, frame: InputFrame, dt: float) -> None:
        del frame, dt

    def start_play(self, filename: str) -> ReplayHeader:
        del filename
        raise RuntimeError("Replay is disabled")

    def next_frame(self) -> ReplayFrame | None:
        return None

    def stop_play(self) -> None:
        return None

    def close(self) -> None:
        return None

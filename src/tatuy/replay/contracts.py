"""Runtime replay capability contract."""

from __future__ import annotations

from typing import Protocol

from tatuy.capture.replay_frame import ReplayFrame
from tatuy.capture.replay_header import ReplayHeader
from tatuy.input.frame import InputFrame


class ReplayCapability(Protocol):
    """Record and play deterministic input independently from media capture."""

    @property
    def enabled(self) -> bool:
        """Whether replay functionality is available."""

    @property
    def recording(self) -> bool:
        """Whether replay recording is active."""

    @property
    def playing(self) -> bool:
        """Whether replay playback is active."""

    @property
    def header(self) -> ReplayHeader | None:
        """Return the active replay header when one exists."""

    def start_record(self, *, filename: str, header: ReplayHeader) -> None:
        """Start recording replay input."""

    def stop_record(self) -> None:
        """Stop replay recording."""

    def record_input(self, frame: InputFrame, dt: float) -> None:
        """Record one input frame when recording is active."""

    def start_play(self, filename: str) -> ReplayHeader:
        """Start replay playback and return its header."""

    def next_frame(self) -> ReplayFrame | None:
        """Return the next replay frame when playback is active."""

    def stop_play(self) -> None:
        """Stop replay playback."""

    def close(self) -> None:
        """Release replay resources."""

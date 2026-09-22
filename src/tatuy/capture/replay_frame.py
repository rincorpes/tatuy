from __future__ import annotations

from dataclasses import dataclass

from tatuy.input.frame import InputFrame


@dataclass(frozen=True)
class ReplayFrame:
    index: int
    dt: float
    input_frame: InputFrame

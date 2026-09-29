from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from math import isfinite

from tatuy.graphics.color import Color, ColorFormatter
from tatuy.graphics.render.overlays import ScreenOverlay


class ScreenEffect(ABC):
    @abstractmethod
    def update(self, dt: float) -> None: ...

    @property
    @abstractmethod
    def finished(self) -> bool: ...

    @abstractmethod
    def snapshot(self) -> tuple[ScreenOverlay, ...]: ...


@dataclass
class FlashEffect(ScreenEffect):
    duration: float
    color: Color = (255, 255, 255)
    peak_alpha: int = 255
    remaining: float = field(init=False)

    def __post_init__(self) -> None:
        if not isfinite(self.duration) or self.duration <= 0:
            raise ValueError("duration must be finite and positive")

        if isinstance(self.peak_alpha, bool) or not isinstance(
            self.peak_alpha, int
        ):
            raise TypeError("peak_alpha must be an integer")

        if not 0 <= self.peak_alpha <= 255:
            raise ValueError("peak_alpha must be in [0, 255]")

        self.color = ColorFormatter.rgba(self.color)
        self.remaining = self.duration

    def update(self, dt: float) -> None:
        if not isfinite(dt) or dt < 0:
            raise ValueError("dt must be finite and nonnegative")

        self.remaining = max(0.0, self.remaining - dt)

    @property
    def finished(self) -> bool:
        return self.remaining <= 0.0

    @property
    def alpha(self) -> int:
        return int(self.peak_alpha * self.remaining / self.duration)

    def snapshot(self) -> tuple[ScreenOverlay, ...]:
        if self.finished:
            return ()

        r, g, b, color_alpha = ColorFormatter.rgba(self.color)
        alpha = round(color_alpha * self.alpha / 255)

        if alpha <= 0:
            return ()

        return (ScreenOverlay(color=(r, g, b, alpha)),)

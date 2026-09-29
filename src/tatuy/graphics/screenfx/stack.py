from __future__ import annotations

from math import isfinite

from tatuy.graphics.color import Color
from tatuy.graphics.render.overlays import ScreenOverlay
from tatuy.graphics.screenfx.effects import FlashEffect, ScreenEffect


class ScreenEffectStack:
    def __init__(self) -> None:
        self._effects: list[ScreenEffect] = []

    @property
    def effects(self) -> tuple[ScreenEffect, ...]:
        return tuple(self._effects)

    def add(self, effect: ScreenEffect) -> None:
        """Transfer ownership of an effect to this stack."""
        if not effect.finished:
            self._effects.append(effect)

    def flash(
        self,
        *,
        duration: float,
        color: Color = (255, 255, 255),
        peak_alpha: int = 255,
    ) -> None:
        flash = FlashEffect(
            duration=duration,
            color=color,
            peak_alpha=peak_alpha,
        )

        # Preserve the strongest active peak for matching colors.
        previous_peak = max(
            (
                effect.peak_alpha
                for effect in self._effects
                if isinstance(effect, FlashEffect)
                and not effect.finished
                and effect.color == flash.color
            ),
            default=0,
        )
        flash.peak_alpha = max(
            flash.peak_alpha,
            previous_peak,
        )

        # The convenience API maintains one flash.
        self._effects[:] = [
            effect
            for effect in self._effects
            if not isinstance(effect, FlashEffect)
        ]
        self.add(flash)

    def update(self, dt: float) -> None:
        if not isfinite(dt) or dt < 0:
            raise ValueError("dt must be finite and nonnegative")

        for effect in self._effects:
            effect.update(dt)

        self._effects[:] = [
            effect for effect in self._effects if not effect.finished
        ]

    def snapshot(self) -> tuple[ScreenOverlay, ...]:
        return tuple(
            overlay
            for effect in self._effects
            for overlay in effect.snapshot()
        )

    def clear(self) -> None:
        self._effects.clear()

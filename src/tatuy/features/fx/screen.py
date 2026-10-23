"""Scene-owned screen effect composition."""

from __future__ import annotations

from math import isfinite

from tatuy.features.fx.screen_effects import FlashEffect, ScreenEffect
from tatuy.graphics.color import Color
from tatuy.graphics.render.overlays import ScreenOverlay


class ScreenEffectStack:
    """Own and update active screen effects for a scene."""

    def __init__(self) -> None:
        self._effects: list[ScreenEffect] = []

    @property
    def effects(self) -> tuple[ScreenEffect, ...]:
        """Return the active effects in insertion order."""
        return tuple(self._effects)

    def add(self, effect: ScreenEffect) -> None:
        """Transfer ownership of an unfinished effect to this stack."""
        if not effect.finished:
            self._effects.append(effect)

    def flash(
        self,
        *,
        duration: float,
        color: Color = (255, 255, 255),
        peak_alpha: int = 255,
    ) -> None:
        """Replace the convenience flash while preserving its strongest peak."""
        flash = FlashEffect(
            duration=duration,
            color=color,
            peak_alpha=peak_alpha,
        )

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

        self._effects[:] = [
            effect
            for effect in self._effects
            if not isinstance(effect, FlashEffect)
        ]
        self.add(flash)

    def update(self, dt: float) -> None:
        """Advance all active effects and remove completed effects."""
        if not isfinite(dt) or dt < 0:
            raise ValueError("dt must be finite and nonnegative")

        for effect in self._effects:
            effect.update(dt)

        self._effects[:] = [
            effect for effect in self._effects if not effect.finished
        ]

    def snapshot(self) -> tuple[ScreenOverlay, ...]:
        """Return the render overlays produced by active effects."""
        return tuple(
            overlay
            for effect in self._effects
            for overlay in effect.snapshot()
        )

    def clear(self) -> None:
        """Remove all active screen effects."""
        self._effects.clear()

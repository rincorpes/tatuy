from __future__ import annotations

from math import cos, isfinite, sin

from tatuy.graphics.camera.transform import ViewTransform


class CameraFX:
    """One scene-owned shake with a linear decay."""

    _remaining: float
    _peak_strength: float
    _decay_duration: float

    def __init__(self) -> None:
        self.clear()

    @property
    def active(self) -> bool:
        return self._remaining > 0.0

    def shake(
        self,
        *,
        duration: float,
        strength: float,
    ) -> None:
        if not isfinite(duration) or duration <= 0:
            raise ValueError("duration must be finite and positive")

        if not isfinite(strength) or strength < 0:
            raise ValueError("strength must be finite and nonnegative")

        if strength == 0:
            return

        self._peak_strength = max(
            self._peak_strength,
            strength,
        )
        self._remaining = max(
            self._remaining,
            duration,
        )
        self._decay_duration = self._remaining

        # Keep the current phase when refreshing an active shake.

    def update(self, dt: float) -> None:
        if not isfinite(dt) or dt < 0:
            raise ValueError("dt must be finite and nonnegative")

        if not self.active:
            return

        self._remaining = max(
            0.0,
            self._remaining - dt,
        )

        if not self.active:
            self.clear()
            return

        self._phase += dt

    def snapshot(self) -> ViewTransform:
        if not self.active:
            return ViewTransform()

        amplitude = (
            self._peak_strength * self._remaining / self._decay_duration
        )

        return ViewTransform(
            offset_x=sin(self._phase * 95.0) * amplitude,
            offset_y=cos(self._phase * 137.0) * amplitude,
        )

    def clear(self) -> None:
        self._remaining = 0.0
        self._decay_duration = 0.0
        self._peak_strength = 0.0
        self._phase = 0.0

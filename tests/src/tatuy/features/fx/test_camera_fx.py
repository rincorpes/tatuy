"""Behavior tests for camera effects."""

import math

import pytest

from tatuy.features.fx.camera import CameraFX
from tatuy.graphics.camera.transform import ViewTransform


def test_camera_fx_is_idle_by_default() -> None:
    fx = CameraFX()

    assert not fx.active
    assert fx.snapshot() == ViewTransform()


def test_camera_fx_shake_updates_and_expires() -> None:
    fx = CameraFX()
    fx.shake(duration=1.0, strength=8.0)

    assert fx.active

    fx.update(0.25)
    snapshot = fx.snapshot()

    assert snapshot != ViewTransform()

    fx.update(0.75)

    assert not fx.active
    assert fx.snapshot() == ViewTransform()


@pytest.mark.parametrize(
    ("duration", "strength"),
    [
        (0.0, 1.0),
        (-1.0, 1.0),
        (math.inf, 1.0),
        (1.0, -1.0),
        (1.0, math.inf),
    ],
)
def test_camera_fx_rejects_invalid_shakes(
    duration: float,
    strength: float,
) -> None:
    fx = CameraFX()

    with pytest.raises(ValueError):
        fx.shake(duration=duration, strength=strength)


def test_camera_fx_rejects_invalid_delta_time() -> None:
    fx = CameraFX()

    with pytest.raises(ValueError):
        fx.update(-0.1)

from __future__ import annotations


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def inverse_lerp(a: float, b: float, value: float) -> float:
    if a == b:
        return 0.0
    return (value - a) / (b - a)


def remap(
    value: float,
    in_min: float,
    in_max: float,
    out_min: float,
    out_max: float,
) -> float:
    t = inverse_lerp(in_min, in_max, value)
    return lerp(out_min, out_max, t)


def _sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def move_towards(
    current: float,
    target: float,
    max_delta: float,
) -> float:
    delta = target - current

    if abs(delta) <= max_delta:
        return target

    return current + _sign(delta) * max_delta

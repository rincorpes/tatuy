from __future__ import annotations

from tatuy.features.movement.components import Movement
from tatuy.math.vec2 import Vec2


class MovementMotor:
    def calculate_velocity(
        self,
        *,
        current: Vec2,
        desired: Vec2,
        movement: Movement,
        dt: float,
    ) -> Vec2:
        direction = self._normalize_direction(desired)

        target = direction * movement.speed

        rate = self._resolve_rate(
            direction,
            movement,
        )

        velocity = (
            target if rate is None else current.move_towards(target, rate * dt)
        )

        return self._clamp_velocity(
            velocity,
            movement.max_speed,
        )

    def _normalize_direction(self, direction: Vec2) -> Vec2:
        if direction.length_squared() <= 1.0:
            return direction

        return direction.normalized()

    def _resolve_rate(
        self,
        direction: Vec2,
        movement: Movement,
    ) -> float:
        if direction.length_squared() > 0:
            return movement.acceleration

        return (
            movement.deceleration
            if movement.deceleration is not None
            else movement.acceleration
        )

    def _clamp_velocity(
        self,
        velocity: Vec2,
        max_speed: float | None,
    ) -> Vec2:
        if max_speed is None:
            return velocity

        if velocity.length_squared() <= max_speed * max_speed:
            return velocity

        return velocity.normalized() * max_speed

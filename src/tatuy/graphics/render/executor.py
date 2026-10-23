"""Replaceable execution boundary for prepared render operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot
from typing import Protocol, Sequence

from tatuy.backend import Backend
from tatuy.graphics.render.commands import (
    CircleCommand,
    LineCommand,
    PolyCommand,
    RectCommand,
    TextCommand,
    TextureCommand,
)
from tatuy.graphics.render.fallback import CustomCommand
from tatuy.graphics.render.queue import PythonRenderOperation, RenderOperation
from tatuy.math.vec2 import Vec2


class RenderExecutor(Protocol):
    """Consume prepared render operations using a rendering backend."""

    def execute(
        self,
        backend: Backend,
        operations: Sequence[RenderOperation],
    ) -> None:
        """Execute a prepared batch while preserving operation order."""


class RenderFallbackExecutor(Protocol):
    """Execute render operations that cannot cross a native boundary."""

    def execute(self, backend: Backend, command: CustomCommand) -> None:
        """Execute one Python-only custom command."""


class PythonCallbackExecutor:
    """Execute the explicit Python callback fallback path."""

    def execute(self, backend: Backend, command: CustomCommand) -> None:
        """Invoke the custom command against the backend."""
        command.op(backend)


class TextCommandRenderer:
    """Render text commands through backend text protocols."""

    def draw(self, command: TextCommand, backend: Backend) -> None:
        """Draw one text command, applying alignment when requested."""
        x = command.x
        y = command.y

        if command.align != "left" or command.valign != "top":
            width, height = backend.renderer.text.measure(
                command.text,
                command.font_size,
                command.font_name,
            )

            if command.align == "center":
                x -= width / 2
            elif command.align == "right":
                x -= width

            if command.valign == "middle":
                y -= height / 2
            elif command.valign == "bottom":
                y -= height

        backend.renderer.text.draw(
            int(x),
            int(y),
            command.text,
            command.color,
            command.font_size,
            command.font_name,
        )


@dataclass
class PythonRenderExecutor:
    """Execute typed render commands through Tatuy's Python backend protocols."""

    fallback: RenderFallbackExecutor = field(
        default_factory=PythonCallbackExecutor
    )

    def execute(
        self,
        backend: Backend,
        operations: Sequence[RenderOperation],
    ) -> None:
        """Execute prepared operations in order."""
        for operation in operations:
            self._execute_operation(backend, operation)

    def _execute_operation(
        self,
        backend: Backend,
        operation: RenderOperation,
    ) -> None:
        if isinstance(operation, PythonRenderOperation):
            if operation.payload is None:
                raise TypeError(
                    "Python render operation requires a fallback payload"
                )
            self.fallback.execute(backend, operation.payload)
            return

        command = operation.payload
        renderer = backend.renderer

        if isinstance(command, RectCommand):
            position = Vec2(
                command.center.x - command.size.width / 2,
                command.center.y - command.size.height / 2,
            )
            renderer.shape.rect(
                position,
                command.size,
                command.color,
                radius=command.radius,
            )
        elif isinstance(command, CircleCommand):
            renderer.shape.circle(
                int(command.center.x),
                int(command.center.y),
                int(command.radius),
                command.color,
            )
        elif isinstance(command, LineCommand):
            self._draw_line(backend, command)
        elif isinstance(command, PolyCommand):
            self._draw_poly(backend, command)
        elif isinstance(command, TextureCommand):
            renderer.texture.draw(
                command.tex_id,
                int(command.x),
                int(command.y),
                int(command.w),
                int(command.h),
                command.angle_deg,
            )
        elif isinstance(command, TextCommand):
            TextCommandRenderer().draw(command, backend)
        else:
            raise TypeError(f"Unsupported draw payload: {command!r}")

    @staticmethod
    def _draw_line(backend: Backend, command: LineCommand) -> None:
        renderer = backend.renderer
        thickness = max(1, int(command.thickness))

        if command.dash_length is None:
            renderer.shape.line(command.a, command.b, command.color, thickness)
            return

        dash = command.dash_length
        gap = command.dash_gap if command.dash_gap is not None else dash
        if dash <= 0 or gap < 0:
            raise ValueError(
                "Dash length must be positive; gap cannot be negative"
            )

        dx = command.b.x - command.a.x
        dy = command.b.y - command.a.y
        length = hypot(dx, dy)
        if length == 0:
            return

        distance = 0.0
        while distance < length:
            end = min(distance + dash, length)
            a = Vec2(
                command.a.x + dx * distance / length,
                command.a.y + dy * distance / length,
            )
            b = Vec2(
                command.a.x + dx * end / length,
                command.a.y + dy * end / length,
            )
            renderer.shape.line(a, b, command.color, thickness)
            distance += dash + gap

    @staticmethod
    def _draw_poly(backend: Backend, command: PolyCommand) -> None:
        renderer = backend.renderer

        if command.fill is not None and len(command.points) >= 3:
            renderer.shape.polygon(
                [(int(point.x), int(point.y)) for point in command.points],
                command.fill,
            )

        if command.stroke is None or len(command.points) < 2:
            return

        edges = list(zip(command.points, command.points[1:]))
        if command.closed:
            edges.append((command.points[-1], command.points[0]))

        for a, b in edges:
            renderer.shape.line(a, b, command.stroke, command.thickness)

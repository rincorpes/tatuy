from __future__ import annotations

from copy import deepcopy
from functools import partial
from math import hypot

from tatuy.backend import Backend
from tatuy.graphics.render.commands import (
    CircleCommand,
    CustomCommand,
    LineCommand,
    PolyCommand,
    RectCommand,
    TextCommand,
    TextureCommand,
)
from tatuy.graphics.render.packets import DrawOp, RenderPacket
from tatuy.graphics.render.queue import DrawOperation, RenderQueue
from tatuy.math.vec2 import Vec2
from tatuy.tooling.profiler import profiler


class TextCommandRenderer:
    def draw(self, command: TextCommand, backend: Backend) -> None:
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


def execute_draw(operation: DrawOperation, backend: Backend) -> None:
    """Execute one prepared command through backend protocols."""
    command = operation.payload
    renderer = backend.renderer
    if isinstance(command, RectCommand):
        position = Vec2(
            command.center.x - command.size.width / 2,
            command.center.y - command.size.height / 2,
        )
        renderer.shape.rect(
            position, command.size, command.color, radius=command.radius
        )
    elif isinstance(command, CircleCommand):
        renderer.shape.circle(
            int(command.center.x),
            int(command.center.y),
            int(command.radius),
            command.color,
        )
    elif isinstance(command, LineCommand):
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
        dx, dy = command.b.x - command.a.x, command.b.y - command.a.y
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
    elif isinstance(command, PolyCommand):
        if command.fill is not None and len(command.points) >= 3:
            renderer.shape.polygon(
                [(int(p.x), int(p.y)) for p in command.points], command.fill
            )
        if command.stroke is not None and len(command.points) >= 2:
            edges = list(zip(command.points, command.points[1:]))
            if command.closed:
                edges.append((command.points[-1], command.points[0]))
            for a, b in edges:
                renderer.shape.line(a, b, command.stroke, command.thickness)
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
    elif isinstance(command, CustomCommand):
        command.op(backend)
    else:
        raise TypeError(f"Unsupported draw payload: {command!r}")


def compile_queue(queue: RenderQueue) -> RenderPacket:
    """Snapshot command values and preserve sorted operations by layer.

    Custom callbacks retain their original identity and captured state; callers
    are responsible for the lifetime of resources referenced by those callbacks.
    """
    ops: list[DrawOp] = []
    pass_ops: dict[str, list[DrawOp]] = {}

    with profiler.span("queue_items", "compile_queue"):
        queue_items = queue.iter_sorted()

    profiler.metric("operations", len(queue_items))

    # with profiler.span("prepare_operations", "compile_queue"):
    #     custom_commands = 0
    #     copied_operations = 0

    #     prepared_operations = []

    #     for operation in queue_items:
    #         if isinstance(operation.payload, CustomCommand):
    #             prepared = operation
    #             custom_commands += 1
    #         else:
    #             prepared = deepcopy(operation)
    #             copied_operations += 1

    #         prepared_operations.append((operation, prepared))

    #     profiler.metric("operations", len(prepared_operations))
    #     profiler.metric("copied_operations", copied_operations)
    #     profiler.metric("custom_commands", custom_commands)

    with profiler.span("build_draw_ops", "compile_queue"):
        for operation in queue_items:  # prepared_operations:
            draw = partial(execute_draw, operation)

            ops.append(draw)
            pass_ops.setdefault(
                operation.layer,
                [],
            ).append(draw)

    with profiler.span("render_packet.from_ops", "compile_queue"):
        return RenderPacket.from_ops(
            ops,
            pass_ops={
                layer: tuple(draws) for layer, draws in pass_ops.items()
            },
        )

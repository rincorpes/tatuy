"""Compile mutable render queues into stable prepared render packets."""

from __future__ import annotations

from copy import deepcopy

from tatuy.graphics.render.commands import CustomCommand
from tatuy.graphics.render.packets import RenderPacket
from tatuy.graphics.render.queue import DrawOperation, RenderQueue
from tatuy.tooling.profiler import profiler


def _snapshot_operation(operation: DrawOperation) -> DrawOperation:
    """Snapshot typed command data while preserving custom callback identity."""
    if isinstance(operation.payload, CustomCommand):
        return DrawOperation(
            kind=operation.kind,
            layer=operation.layer,
            z=operation.z,
            seq=operation.seq,
            payload=operation.payload,
        )

    return deepcopy(operation)


def compile_queue(queue: RenderQueue) -> RenderPacket:
    """Compile sorted queue operations into stable rendering data.

    Typed commands are deep-copied so later mutation of gameplay vectors or
    sizes cannot change an already compiled frame. ``CustomCommand`` remains
    an explicit Python fallback and therefore retains its callback and captured
    state by reference.
    """
    with profiler.span("queue_items", "compile_queue"):
        queue_items = queue.iter_sorted()

    profiler.metric("operations", len(queue_items))

    with profiler.span("snapshot_operations", "compile_queue"):
        operations = tuple(_snapshot_operation(item) for item in queue_items)

    custom_commands = sum(
        isinstance(operation.payload, CustomCommand)
        for operation in operations
    )
    profiler.metric("custom_commands", custom_commands)
    profiler.metric("typed_operations", len(operations) - custom_commands)

    return RenderPacket(operations=operations)

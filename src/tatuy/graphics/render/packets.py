from __future__ import annotations
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Callable

from tatuy.backend import Backend

DrawOp = Callable[[Backend], None]


@dataclass(frozen=True)
class RenderPacket:
    """
    Minimal render packet for v1.

    It is intentionally backend-agnostic: each op is a callable that knows
    how to draw itself using the Backend instance.

    Later you can replace DrawOp with typed primitives + passes.
    """

    ops: tuple[DrawOp, ...] = ()
    meta: dict[str, object] = field(default_factory=dict)

    @staticmethod
    def from_ops(ops: Iterable[DrawOp], **meta: object) -> "RenderPacket":
        """
        Create a RenderPacket from an iterable of DrawOps and optional meta.

        :param ops: Iterable of DrawOp callables.
        :type ops: Iterable[DrawOp]

        :return: RenderPacket instance.
        :rtype: RenderPacket
        """
        return RenderPacket(ops=tuple(ops), meta=dict(meta))

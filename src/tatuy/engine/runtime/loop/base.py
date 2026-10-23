"""Runtime loop contract."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from tatuy.engine.engine import Engine


class RuntimeLoop(Protocol):
    """Drive an engine session until it stops running."""

    def run(self, engine: Engine) -> None:
        """Start, step, and stop an engine session."""

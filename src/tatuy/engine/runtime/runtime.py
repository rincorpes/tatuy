"""Runtime host for an engine and its execution loop."""

from __future__ import annotations

from dataclasses import dataclass

from tatuy.engine.engine import Engine
from tatuy.engine.runtime.loop.base import RuntimeLoop


@dataclass(slots=True)
class Runtime:
    """Host an engine with a replaceable execution loop."""

    engine: Engine
    loop: RuntimeLoop

    def run(self) -> None:
        """Run the hosted engine through the configured loop."""
        self.loop.run(self.engine)

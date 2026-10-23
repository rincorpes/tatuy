"""Runtime host for an engine and its execution loop."""

from __future__ import annotations

from dataclasses import dataclass

from tatuy.engine.engine import Engine
from tatuy.engine.runtime.loop.base import AsyncRuntimeLoop, RuntimeLoop


@dataclass(slots=True)
class Runtime:
    """Host an engine with a replaceable synchronous execution loop."""

    engine: Engine
    loop: RuntimeLoop

    def run(self) -> None:
        """Run the hosted engine through the configured loop."""
        self.loop.run(self.engine)


@dataclass(slots=True)
class AsyncRuntime:
    """Host an engine with a replaceable asynchronous execution loop."""

    engine: Engine
    loop: AsyncRuntimeLoop

    async def run(self) -> None:
        """Run the hosted engine while yielding through the configured loop."""
        await self.loop.run(self.engine)

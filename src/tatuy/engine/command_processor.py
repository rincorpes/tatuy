from __future__ import annotations

from tatuy.commands import EngineCommandContext, EngineCommandQueue


class EngineCommandProcessor:
    def __init__(self, engine, backend, queue: EngineCommandQueue):
        self._engine = engine
        self._backend = backend
        self._queue = queue

    def process(self) -> None:
        context = EngineCommandContext(
            engine=self._engine,
            window=self._backend.window,
        )

        for command in self._queue.drain():
            command.execute(context)

            if context.end_batch or not self._engine.running:
                break

        if self._engine.running:
            self._backend.input.set_cursor(context.cursor)

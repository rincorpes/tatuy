"""Asyncio-hosted runtime loop implementation for browser-compatible hosts."""

from __future__ import annotations

from asyncio import sleep
from collections.abc import Callable

from tatuy.engine.engine import Engine
from tatuy.engine.runtime.loop.clock import FrameClock


class AsyncioLoop:
    """Run an engine session while yielding once per frame to the host loop."""

    def __init__(self) -> None:
        self._first_frame_callback: Callable[[], None] | None = None

    def set_first_frame_callback(self, callback: Callable[[], None] | None) -> None:
        """Set an optional callback fired after the first completed engine frame."""
        self._first_frame_callback = callback

    async def run(self, engine: Engine) -> None:
        """Run the engine with Python-loop cleanup semantics and async yielding."""
        try:
            engine.start()
            clock = FrameClock()
            first_frame_pending = True

            while engine.running:
                clock.step_time()
                engine.step(clock.dt, clock.frame_index)
                if first_frame_pending:
                    first_frame_pending = False
                    callback = self._first_frame_callback
                    if callback is not None:
                        callback()
                clock.frame_index += 1
                await sleep(0)
        except BaseException as run_error:
            try:
                engine.stop()
            except BaseException as cleanup_error:
                raise run_error from cleanup_error
            raise

        engine.stop()

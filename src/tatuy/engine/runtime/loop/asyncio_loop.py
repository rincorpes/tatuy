"""Asyncio-hosted runtime loop implementation for browser-compatible hosts."""

from __future__ import annotations

from asyncio import sleep

from tatuy.engine.engine import Engine
from tatuy.engine.runtime.loop.clock import FrameClock


class AsyncioLoop:
    """Run an engine session while yielding once per frame to the host loop."""

    async def run(self, engine: Engine) -> None:
        """Run the engine with Python-loop cleanup semantics and async yielding."""
        try:
            engine.start()
            clock = FrameClock()

            while engine.running:
                clock.step_time()
                engine.step(clock.dt, clock.frame_index)
                clock.frame_index += 1
                await sleep(0)
        except BaseException as run_error:
            try:
                engine.stop()
            except BaseException as cleanup_error:
                raise run_error from cleanup_error
            raise

        engine.stop()

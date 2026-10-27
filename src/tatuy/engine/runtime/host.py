"""Execution hosts for configured Tatuy runtime sessions."""

from __future__ import annotations

import gc
from typing import cast

from tatuy.engine.runtime.loop.base import AsyncRuntimeLoop, RuntimeLoop
from tatuy.engine.runtime.runtime import Runtime
from tatuy.tooling.profiler import profiler
from tatuy.tooling.profiler.export import export_profile


class SyncRuntimeHost:
    """Execute a runtime whose configured loop is synchronous."""

    def run(self, runtime: Runtime) -> None:
        """Run a synchronous runtime with shared session cleanup semantics."""
        if runtime.mode != "sync":
            raise TypeError(
                "SyncRuntimeHost requires a runtime configured with a sync loop"
            )

        loop = cast(RuntimeLoop, runtime.loop)
        gc.disable()
        try:
            loop.run(runtime.engine)
        finally:
            _finalize_run()


class AsyncRuntimeHost:
    """Execute a runtime whose configured loop cooperates with an async host."""

    async def run(self, runtime: Runtime) -> None:
        """Run an asynchronous runtime with shared session cleanup semantics."""
        if runtime.mode != "async":
            raise TypeError(
                "AsyncRuntimeHost requires a runtime configured with an async loop"
            )

        loop = cast(AsyncRuntimeLoop, runtime.loop)
        gc.disable()
        try:
            await loop.run(runtime.engine)
        finally:
            _finalize_run()


def _finalize_run() -> None:
    """Restore GC state and emit profiler output after a runtime session."""
    gc.collect()
    gc.enable()

    if not profiler.enabled:
        return

    snapshot = profiler.snapshot()
    export_profile(snapshot, ".tatuy/profiles/latest.json")
    print(profiler.report())
    print("\nSlowest frames")
    print(profiler.format_slowest("frame", limit=3))
    print("Profile written to profiles/latest.json")

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from tatuy.engine.runtime import host as host_module
from tatuy.engine.runtime.host import AsyncRuntimeHost, SyncRuntimeHost
from tatuy.engine.runtime.runtime import Runtime


def test_sync_host_runs_configured_loop_and_finalizes(monkeypatch):
    engine = Mock()
    loop = Mock()
    finalize = Mock()
    monkeypatch.setattr(host_module, "_finalize_run", finalize)
    runtime = Runtime(engine=engine, loop=loop, mode="sync")

    SyncRuntimeHost().run(runtime)

    loop.run.assert_called_once_with(engine)
    finalize.assert_called_once_with()


def test_sync_host_rejects_async_runtime(monkeypatch):
    finalize = Mock()
    monkeypatch.setattr(host_module, "_finalize_run", finalize)
    runtime = Runtime(engine=Mock(), loop=Mock(), mode="async")

    with pytest.raises(TypeError, match="sync loop"):
        SyncRuntimeHost().run(runtime)

    finalize.assert_not_called()


def test_async_host_runs_configured_loop_and_finalizes(monkeypatch):
    engine = Mock()
    loop = Mock()
    loop.run = AsyncMock()
    finalize = Mock()
    monkeypatch.setattr(host_module, "_finalize_run", finalize)
    runtime = Runtime(engine=engine, loop=loop, mode="async")

    asyncio.run(AsyncRuntimeHost().run(runtime))

    loop.run.assert_awaited_once_with(engine)
    finalize.assert_called_once_with()


def test_async_host_rejects_sync_runtime(monkeypatch):
    finalize = Mock()
    monkeypatch.setattr(host_module, "_finalize_run", finalize)
    runtime = Runtime(engine=Mock(), loop=Mock(), mode="sync")

    with pytest.raises(TypeError, match="async loop"):
        asyncio.run(AsyncRuntimeHost().run(runtime))

    finalize.assert_not_called()

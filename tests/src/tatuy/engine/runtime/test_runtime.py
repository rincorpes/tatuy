import asyncio
from unittest.mock import AsyncMock, Mock

from tatuy.engine.runtime.runtime import AsyncRuntime, Runtime


def test_run_delegates_engine_to_configured_loop():
    engine = Mock()
    loop = Mock()
    runtime = Runtime(engine=engine, loop=loop)

    runtime.run()

    loop.run.assert_called_once_with(engine)


def test_async_run_delegates_engine_to_configured_loop():
    engine = Mock()
    loop = Mock()
    loop.run = AsyncMock()
    runtime = AsyncRuntime(engine=engine, loop=loop)

    asyncio.run(runtime.run())

    loop.run.assert_awaited_once_with(engine)

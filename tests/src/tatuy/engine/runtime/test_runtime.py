from unittest.mock import Mock

from tatuy.engine.runtime.runtime import Runtime


def test_run_delegates_engine_to_configured_loop():
    engine = Mock()
    loop = Mock()
    runtime = Runtime(engine=engine, loop=loop)

    runtime.run()

    loop.run.assert_called_once_with(engine)

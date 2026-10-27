from unittest.mock import Mock

from tatuy.engine.runtime.runtime import Runtime


def test_runtime_records_synchronous_execution_mode():
    engine = Mock()
    loop = Mock()

    runtime = Runtime(engine=engine, loop=loop, mode="sync")

    assert runtime.engine is engine
    assert runtime.loop is loop
    assert runtime.mode == "sync"


def test_runtime_records_asynchronous_execution_mode():
    engine = Mock()
    loop = Mock()

    runtime = Runtime(engine=engine, loop=loop, mode="async")

    assert runtime.engine is engine
    assert runtime.loop is loop
    assert runtime.mode == "async"

from __future__ import annotations

from dataclasses import dataclass
from tatuy.engine.engine import Engine
from tatuy.engine.loop.python_loop import PythonLoop


@dataclass(slots=True)
class Runtime:
    engine: Engine
    loop: PythonLoop

    def run(self) -> None:
        self.loop.run(self.engine)

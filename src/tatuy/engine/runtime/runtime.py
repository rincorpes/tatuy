"""Runtime composition shared by synchronous and cooperative hosts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias

from tatuy.engine.engine import Engine
from tatuy.engine.runtime.loop.base import AsyncRuntimeLoop, RuntimeLoop

RuntimeMode: TypeAlias = Literal["sync", "async"]
RuntimeLoopType: TypeAlias = RuntimeLoop | AsyncRuntimeLoop


@dataclass(slots=True)
class Runtime:
    """Pair an engine with the configured loop and its host execution mode."""

    engine: Engine
    loop: RuntimeLoopType
    mode: RuntimeMode

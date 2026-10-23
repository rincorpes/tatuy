"""Explicit Python-only render fallback types.

These callbacks are intentionally excluded from the native-compatible draw
command stream. They may depend on Tatuy's Python backend and must be routed or
rejected explicitly by future native executors.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from tatuy.backend.protocols import Renderer


class PythonRenderContext(Protocol):
    """Minimal rendering capability exposed to Python fallback callbacks."""

    @property
    def renderer(self) -> Renderer:
        """Return the renderer capability available to the callback."""


PythonRenderCallback = Callable[[PythonRenderContext], None]


@dataclass(frozen=True, slots=True)
class CustomCommand:
    """Python-only rendering callback that cannot cross a native ABI."""

    op: PythonRenderCallback

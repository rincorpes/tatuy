"""Platform-neutral capability contracts consumed by Tatuy services."""

from __future__ import annotations

from .audio import Audio
from .capture import Capture
from .events import Events
from .input import Input
from .renderer import Renderer
from .window import Window

__all__ = [
    "Audio",
    "Capture",
    "Events",
    "Input",
    "Renderer",
    "Window",
]

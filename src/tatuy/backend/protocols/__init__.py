"""
Backend module for rendering and input abstraction.
Defines the Backend interface and related types.
This is the only part of the code that talks to SDL/pygame directly.
"""

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

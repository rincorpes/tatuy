"""Structural contract for the platform capabilities used by the engine."""

from __future__ import annotations

from typing import Protocol

from tatuy.backend.config import BackendConfig
from tatuy.graphics.viewport.transform import ViewportTransform

from .protocols import Audio, Capture, Events, Input, Renderer, Window


class Backend(Protocol):
    """Expose the configuration, capabilities, and lifecycle required by the engine.

    Attributes:
        viewport_transform (ViewportTransform): Mapping between logical
            coordinates and display pixels.
        initialized (bool): Whether platform startup has completed
            successfully.
    """

    @property
    def config(self) -> BackendConfig:
        """Return the immutable configuration used to construct this backend.

        Returns:
            BackendConfig: The requested capability.
        """

    @property
    def events(self) -> Events:
        """Return the event collection capability.

        Returns:
            Events: The requested capability.
        """

    @property
    def window(self) -> Window:
        """Return the portable window management capability.

        Returns:
            Window: The requested capability.
        """

    @property
    def audio(self) -> Audio:
        """Return the sound playback and volume capability.

        Returns:
            Audio: The requested capability.
        """

    @property
    def capture(self) -> Capture:
        """Return the explicit image and raw-frame capture capability.

        Returns:
            Capture: The requested capability.
        """

    @property
    def input(self) -> Input:
        """Return the pointer observation and cursor capability.

        Returns:
            Input: The requested capability.
        """

    @property
    def renderer(self) -> Renderer:
        """Return the drawing and frame presentation capability.

        Returns:
            Renderer: The requested capability.
        """

    viewport_transform: ViewportTransform
    initialized: bool

    def init(self) -> None:
        """Initialize platform state and prepare the configured capabilities.

        Returns:
            None: This method does not return a value.
        """

    def stop(self) -> None:
        """Release platform resources owned by this backend.

        Returns:
            None: This method does not return a value.
        """

from __future__ import annotations

from typing import Protocol

from tatuy.backend.config import BackendConfig
from tatuy.graphics.viewport.transform import ViewportTransform

from .protocols import Audio, Capture, Events, Input, Renderer, Window


class Backend(Protocol):
    """
    Interface that any rendering/input backend must implement.
    tatuy-core only talks to this protocol, never to SDL/pygame directly.

    Each sub-capability is exposed as a typed protocol attribute so that
    systems or draw helpers can accept only the slice they need (e.g.
    ``Renderer`` or ``Text``) instead of the full backend.
    """

    @property
    def config(self) -> BackendConfig: ...

    @property
    def events(self) -> Events: ...

    @property
    def window(self) -> Window: ...

    @property
    def audio(self) -> Audio: ...

    @property
    def capture(self) -> Capture: ...

    @property
    def input(self) -> Input: ...

    @property
    def renderer(self) -> Renderer: ...

    viewport_transform: ViewportTransform
    initialized: bool

    def init(self) -> None: ...
    def stop(self) -> None: ...

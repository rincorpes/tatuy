"""Common configuration storage for concrete backend capabilities."""

from __future__ import annotations

from typing import Generic

from tatuy.backend.config import ConfigT


class BackendComponent(Generic[ConfigT]):
    """Store the typed configuration shared by a concrete capability.

    Args:
        config (ConfigT): Settings used to configure this capability.
    """

    def __init__(self, config: ConfigT):
        self.config = config

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(config={self.config})"

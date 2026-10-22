"""Builder interface and registry for named backend implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from onomasticon import ImplementationRegistry

from tatuy.backend.backend import Backend


class BackendBuilder(ABC):
    """Decode implementation-specific settings and construct a backend."""

    @abstractmethod
    def build(self, config: dict[str, Any]) -> Backend:
        """Construct an uninitialized backend from implementation-specific settings.

        Args:
            config (dict[str, Any]): Settings used to configure this
                capability.

        Returns:
            Backend: Uninitialized backend using the decoded configuration.
        """


class BackendRegistry(ImplementationRegistry[BackendBuilder]):
    """Register backend builders by their normalized implementation names."""

    implementation_base = BackendBuilder

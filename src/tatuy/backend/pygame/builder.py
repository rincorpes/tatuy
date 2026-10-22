"""Register and construct the Pygame backend from configuration dictionaries."""

from __future__ import annotations

from typing import Any, cast

from tatuy.backend.backend import Backend
from tatuy.backend.pygame.config import PygameBackendConfig
from tatuy.backend.pygame.pygame_backend import PygameBackend
from tatuy.backend.registry import BackendBuilder, BackendRegistry


@BackendRegistry.implementation("pygame")
class PygameBackendBuilder(BackendBuilder):
    """Build the registered Pygame backend without opening platform devices."""

    def build(self, config: dict[str, Any]) -> Backend:
        """Decode Pygame settings and return a backend without initializing devices.

        Args:
            config (dict[str, Any]): Dictionary of Pygame backend settings.

        Returns:
            Backend: Uninitialized backend using the decoded configuration.

        Raises:
            BackendConfigError: The configuration dictionary cannot be decoded.
        """
        backend_config = PygameBackendConfig.from_dict(config)

        # Validates the result and narrows its type without Self.
        if not isinstance(backend_config, PygameBackendConfig):
            raise TypeError("Expected PygameBackendConfig")

        return cast(Backend, PygameBackend(backend_config))

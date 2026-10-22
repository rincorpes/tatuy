"""Construct registered backends, discovering their builders on demand."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from tatuy.backend.backend import Backend
from tatuy.backend.registry import BackendRegistry


class BackendFactory:
    """Create uninitialized backend instances through registered builders."""

    @classmethod
    def create(cls, name: str, config: dict[str, Any]) -> Backend:
        """Construct an uninitialized backend for the normalized implementation name.

        Discover an unregistered implementation by importing its builder module.
        Raise ValueError for invalid or unknown names and missing registrations;
        preserve missing dependency and configuration errors from the builder.

        Args:
            name (str): Backend implementation name, normalized by trimming
                whitespace and folding case.
            config (dict[str, Any]): Settings used to configure this
                capability.

        Returns:
            Backend: New uninitialized backend instance.

        Raises:
            ValueError: The name is invalid, unavailable, or has no registered
                builder.
            ModuleNotFoundError: A backend dependency cannot be imported.
            BackendConfigError: The selected builder rejects the configuration.
        """
        name = name.strip().casefold()

        if not BackendRegistry.contains(name):
            if not name.isidentifier() or name.startswith("_"):
                raise ValueError(f"Invalid backend name: {name!r}")

            package = f"tatuy.backend.{name}"
            module = f"{package}.builder"

            try:
                import_module(module)
            except ModuleNotFoundError as exc:
                if exc.name in {package, module}:
                    raise ValueError(f"Unknown backend: {name!r}") from exc

                # Preserve errors for missing backend dependencies.
                raise

        try:
            builder_type = BackendRegistry.get(name)
        except KeyError as exc:
            raise ValueError(
                f"Builder module did not register backend {name!r}"
            ) from exc

        return builder_type().build(config)

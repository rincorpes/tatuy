from __future__ import annotations

from importlib import import_module
from typing import Any

from tatuy.backend.backend import Backend
from tatuy.backend.registry import BackendRegistry


class BackendFactory:
    @classmethod
    def create(cls, name: str, config: dict[str, Any]) -> Backend:
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

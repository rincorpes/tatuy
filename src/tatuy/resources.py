from __future__ import annotations

from typing import TypeVar, cast

TResource = TypeVar("TResource")


class ResourceStore:
    def __init__(self) -> None:
        self._resources: dict[type, object] = {}

    def add(self, resource: TResource) -> TResource:
        resource_type = type(resource)

        if resource_type in self._resources:
            raise ValueError(
                f"Resource {resource_type.__name__} " "is already registered"
            )

        self._resources[resource_type] = resource
        return resource

    def get(self, resource_type: type[TResource]) -> TResource:
        try:
            resource = self._resources[resource_type]
        except KeyError as exc:
            raise KeyError(
                f"Resource {resource_type.__name__} " "is not registered"
            ) from exc

        return cast(TResource, resource)

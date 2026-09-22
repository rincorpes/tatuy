from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from onomasticon import ImplementationRegistry

from tatuy.backend.backend import Backend


class BackendBuilder(ABC):
    @abstractmethod
    def build(self, config: dict[str, Any]) -> Backend: ...


class BackendRegistry(ImplementationRegistry[BackendBuilder]):
    implementation_base = BackendBuilder

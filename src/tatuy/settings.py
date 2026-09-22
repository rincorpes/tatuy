from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

import onomasticon

TSettings = TypeVar("TSettings")


class SettingsBuilder(ABC, Generic[TSettings]):
    @abstractmethod
    def build(self, config: dict[str, Any]) -> TSettings: ...


class SettingsRegistry(onomasticon.ImplementationRegistry[SettingsBuilder]):
    implementation_base = SettingsBuilder

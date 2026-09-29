from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

import onomasticon

from tatuy.dataclass_utils import dataclass_from_dict

TSettings = TypeVar("TSettings")


class DataclassSettings:
    @classmethod
    def from_dict(
        cls: type[TSettings],
        data: dict[str, Any],
    ) -> TSettings:
        return dataclass_from_dict(cls, data)


class SettingsBuilder(ABC, Generic[TSettings]):
    @abstractmethod
    def build(self, config: dict[str, Any]) -> TSettings: ...


class SettingsRegistry(onomasticon.ImplementationRegistry[SettingsBuilder]):
    implementation_base = SettingsBuilder

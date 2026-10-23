"""Public scene authoring API with lazy imports to avoid package cycles."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tatuy.scenes.context import Intent, SceneContext, SceneTickContext
    from tatuy.scenes.registry import SceneRegistry
    from tatuy.scenes.scene import EntitySpawn, Scene

_EXPORTS = {
    "EntitySpawn": ("tatuy.scenes.scene", "EntitySpawn"),
    "Intent": ("tatuy.scenes.context", "Intent"),
    "Scene": ("tatuy.scenes.scene", "Scene"),
    "SceneContext": ("tatuy.scenes.context", "SceneContext"),
    "SceneRegistry": ("tatuy.scenes.registry", "SceneRegistry"),
    "SceneTickContext": ("tatuy.scenes.context", "SceneTickContext"),
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    try:
        module_name, attribute = _EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(name) from exc

    value = getattr(import_module(module_name), attribute)
    globals()[name] = value
    return value

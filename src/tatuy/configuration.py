"""Layered Tatuy configuration loading and deterministic merging."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping

ConfigMapping = Mapping[str, Any]
ConfigDict = dict[str, Any]


def merge_config(base: ConfigMapping, override: ConfigMapping) -> ConfigDict:
    """Deep-merge two configuration mappings without mutating either input.

    Nested mappings merge recursively. Scalars and lists replace the existing
    value completely so configuration precedence remains explicit.
    """
    merged: ConfigDict = deepcopy(dict(base))

    for key, value in override.items():
        existing = merged.get(key)
        if isinstance(existing, Mapping) and isinstance(value, Mapping):
            merged[key] = merge_config(existing, value)
        else:
            merged[key] = deepcopy(value)

    return merged


class ConfigurationLoader:
    """Load a base YAML mapping and optional higher-precedence overlays."""

    @classmethod
    def load(
        cls,
        path: str | Path,
        *,
        overlays: Iterable[str | Path] = (),
    ) -> ConfigDict:
        """Load one base YAML file and merge overlays from left to right."""
        config = cls._load_yaml(Path(path))
        for overlay in overlays:
            config = merge_config(config, cls._load_yaml(Path(overlay)))
        return config

    @classmethod
    def load_profile(
        cls,
        path: str | Path,
        profile: str,
    ) -> ConfigDict:
        """Load optional base config plus a sibling profile overlay."""
        base_path = Path(path)
        config = cls._load_yaml(base_path) if base_path.exists() else {}
        profile_path = base_path.with_name(
            f"{base_path.stem}.{profile}{base_path.suffix}"
        )
        if profile_path.exists():
            config = merge_config(config, cls._load_yaml(profile_path))
        return config

    @staticmethod
    def _load_yaml(path: Path) -> ConfigDict:
        if not path.exists():
            raise FileNotFoundError(path)

        try:
            import yaml  # type: ignore[import-untyped]  # pylint: disable=import-outside-toplevel
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "YAML configuration requires PyYAML. Install Tatuy with the "
                "'config' extra."
            ) from exc

        with path.open("r", encoding="utf-8") as stream:
            loaded = yaml.safe_load(stream)

        if loaded is None:
            return {}
        if not isinstance(loaded, dict):
            raise TypeError(
                f"Configuration file {path} must contain a top-level mapping"
            )
        return dict(loaded)

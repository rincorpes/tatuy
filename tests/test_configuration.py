"""Tests for layered Tatuy configuration loading."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tatuy.configuration import ConfigurationLoader, merge_config


def test_merge_config_recursively_merges_mappings_and_replaces_lists():
    base = {
        "app": {"backend": "pygame", "loop": "python"},
        "engine": {"fps": 60},
        "plugins": ["desktop"],
    }
    override = {
        "app": {"loop": "asyncio"},
        "capabilities": {"capture": False},
        "plugins": ["web"],
    }

    merged = merge_config(base, override)

    assert merged == {
        "app": {"backend": "pygame", "loop": "asyncio"},
        "engine": {"fps": 60},
        "capabilities": {"capture": False},
        "plugins": ["web"],
    }
    assert base["app"]["loop"] == "python"
    assert override["app"]["loop"] == "asyncio"


def test_load_profile_merges_existing_profile_overlay(
    tmp_path: Path, monkeypatch
):
    base_path = tmp_path / "tatuy.yml"
    profile_path = tmp_path / "tatuy.web.yml"
    base_path.touch()
    profile_path.touch()

    values = {
        base_path: {"app": {"backend": "pygame", "loop": "python"}},
        profile_path: {
            "app": {"loop": "asyncio"},
            "capabilities": {"capture": False},
        },
    }
    monkeypatch.setattr(
        ConfigurationLoader,
        "_load_yaml",
        staticmethod(lambda path: values[path]),
    )

    config = ConfigurationLoader.load_profile(base_path, "web")

    assert config["app"] == {"backend": "pygame", "loop": "asyncio"}
    assert config["capabilities"] == {"capture": False}


def test_load_profile_uses_base_when_overlay_is_missing(
    tmp_path: Path, monkeypatch
):
    base_path = tmp_path / "tatuy.yml"
    base_path.touch()
    monkeypatch.setattr(
        ConfigurationLoader,
        "_load_yaml",
        staticmethod(lambda path: {"engine": {"fps": 60}}),
    )

    config = ConfigurationLoader.load_profile(base_path, "web")

    assert config == {"engine": {"fps": 60}}


def test_load_profile_uses_overlay_when_base_is_missing(
    tmp_path: Path, monkeypatch
):
    base_path = tmp_path / "tatuy.yml"
    profile_path = tmp_path / "tatuy.web.yml"
    profile_path.touch()
    monkeypatch.setattr(
        ConfigurationLoader,
        "_load_yaml",
        staticmethod(lambda path: {"app": {"loop": "asyncio"}}),
    )

    config = ConfigurationLoader.load_profile(base_path, "web")

    assert config == {"app": {"loop": "asyncio"}}


def test_yaml_loader_uses_safe_load_and_requires_mapping(
    tmp_path: Path, monkeypatch
):
    path = tmp_path / "tatuy.yml"
    path.write_text("app:\n  loop: python\n", encoding="utf-8")
    fake_yaml = SimpleNamespace(safe_load=lambda stream: [stream.read()])
    monkeypatch.setitem(sys.modules, "yaml", fake_yaml)

    with pytest.raises(TypeError, match="top-level mapping"):
        ConfigurationLoader._load_yaml(path)


def test_yaml_loader_returns_mapping_from_pyyaml(tmp_path: Path, monkeypatch):
    path = tmp_path / "tatuy.yml"
    path.write_text("app:\n  loop: python\n", encoding="utf-8")
    fake_yaml = SimpleNamespace(
        safe_load=lambda stream: {"app": {"loop": "python"}}
    )
    monkeypatch.setitem(sys.modules, "yaml", fake_yaml)

    config = ConfigurationLoader._load_yaml(path)

    assert config == {"app": {"loop": "python"}}

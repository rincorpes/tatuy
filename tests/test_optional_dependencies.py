"""Packaging-level checks for Tatuy's optional dependency boundaries."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_public_core_imports_without_optional_dependencies() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    source_root = repository_root / "src"

    code = r"""
import importlib.abc
import sys

BLOCKED = ("pygame", "PIL", "mcp", "limen", "dotenv", "relict")


class OptionalDependencyBlocker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if any(fullname == name or fullname.startswith(name + ".") for name in BLOCKED):
            raise ModuleNotFoundError(
                f"blocked optional dependency: {fullname}",
                name=fullname,
            )
        return None


sys.meta_path.insert(0, OptionalDependencyBlocker())

import tatuy
from tatuy import TatuyApp, TatuyConfigDict
from tatuy.capture.worker import CaptureWorker
from tatuy.ecs import World
from tatuy.features.visual import Rect
from tatuy.scenes import Scene

assert tatuy.__all__ == ["TatuyApp", "TatuyConfigDict"]
assert TatuyApp() is not None
assert TatuyConfigDict is not None
assert CaptureWorker is not None
assert World is not None
assert Rect is not None
assert Scene is not None
"""

    environment = os.environ.copy()
    existing_pythonpath = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        str(source_root)
        if not existing_pythonpath
        else os.pathsep.join((str(source_root), existing_pythonpath))
    )

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=repository_root,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_disabled_capture_does_not_import_concrete_capture_stack() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    source_root = repository_root / "src"

    code = r"""
import importlib.abc
import sys

BLOCKED = (
    "tatuy.capture.service",
    "tatuy.capture.worker",
    "tatuy.capture.video",
    "tatuy.capture.video_encoder",
)


class CaptureImplementationBlocker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if any(fullname == name or fullname.startswith(name + ".") for name in BLOCKED):
            raise ModuleNotFoundError(
                f"blocked concrete capture implementation: {fullname}",
                name=fullname,
            )
        return None


sys.meta_path.insert(0, CaptureImplementationBlocker())

from tatuy import TatuyApp

app = TatuyApp({"capabilities": {"capture": False}})
capture = app.create_capture(object())
assert capture.enabled is False
"""

    environment = os.environ.copy()
    existing_pythonpath = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        str(source_root)
        if not existing_pythonpath
        else os.pathsep.join((str(source_root), existing_pythonpath))
    )

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=repository_root,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

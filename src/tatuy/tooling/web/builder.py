"""Reusable Tatuy web-target staging, packaging, and normalization."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
from typing import Any, Mapping

from tatuy.configuration import ConfigurationLoader, merge_config
from tatuy.tooling.web.models import WebBuildResult, WebShowcaseMetadata
from tatuy.tooling.web.pygbag import BrowserPackager, PygbagPackager

DEFAULT_RUNTIME_OVERRIDES: dict[str, Any] = {
    "backend": {"audio": {"enabled": False, "auto_init": False}},
    "capabilities": {"capture": False, "replay": False},
    "storage": {"provider": "ephemeral"},
}


class WebTargetBuilder:
    """Build browser-playable Tatuy targets without Pygbag knowledge in gameplay.

    Args:
        repository_root: Tatuy repository root used to resolve relative targets.
        staging_root: Ignored content-addressed staging directory.
        output_root: Normalized static output root containing ``play/``.
        tatuy_source: Tatuy source package directory bundled with the target.
        pure_python_packages: Additional importable packages to bundle.
        runtime_overrides: Host-owned configuration merged after target profiles.
        packager: Browser packaging backend.
    """

    def __init__(
        self,
        repository_root: Path,
        *,
        staging_root: Path | None = None,
        output_root: Path | None = None,
        tatuy_source: Path | None = None,
        pure_python_packages: tuple[str, ...] = ("onomasticon",),
        runtime_overrides: Mapping[str, Any] | None = None,
        packager: BrowserPackager | None = None,
    ) -> None:
        self.repository_root = repository_root.resolve()
        self.staging_root = (
            staging_root or self.repository_root / ".tatuy" / "web-staging"
        ).resolve()
        self.output_root = (
            output_root or self.repository_root / "build" / "web"
        ).resolve()
        self.tatuy_source = (
            tatuy_source or self.repository_root / "src" / "tatuy"
        ).resolve()
        self.pure_python_packages = pure_python_packages
        self.runtime_overrides = dict(
            runtime_overrides or DEFAULT_RUNTIME_OVERRIDES
        )
        self.packager = packager or PygbagPackager()

    def resolve_target(self, target: str | Path) -> Path:
        """Resolve and validate one Tatuy target directory.

        Args:
            target: Repository-relative or absolute target directory.

        Returns:
            Resolved target directory containing ``app.py``.

        Raises:
            ValueError: The target escapes the repository root.
            FileNotFoundError: The target directory or ``app.py`` is missing.
        """
        candidate = Path(target)
        if not candidate.is_absolute():
            candidate = self.repository_root / candidate
        resolved = candidate.resolve()
        try:
            resolved.relative_to(self.repository_root)
        except ValueError as exc:
            raise ValueError(
                "Web target must be inside the repository"
            ) from exc
        if not resolved.is_dir():
            raise FileNotFoundError(
                f"Web target directory not found: {resolved}"
            )
        if not (resolved / "app.py").is_file():
            raise FileNotFoundError(f"Web target has no app.py: {resolved}")
        return resolved

    def prepare(self, target: str | Path) -> tuple[Path, WebShowcaseMetadata]:
        """Stage one target and return its staging directory and metadata.

        Args:
            target: Repository-relative or absolute target directory.

        Returns:
            Tuple containing the content-addressed staging path and metadata.
        """
        resolved = self.resolve_target(target)
        config, metadata = self._load_target_config(resolved)
        build_id = self._content_fingerprint(resolved)
        self.staging_root.mkdir(parents=True, exist_ok=True)
        staging = self.staging_root / f"{metadata.slug}-{build_id}"
        for stale in self.staging_root.glob(f"{metadata.slug}-*"):
            if stale != staging and stale.is_dir():
                shutil.rmtree(stale)
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir()
        self._copy_target(resolved, staging)
        self._copy_tatuy(staging)
        for package_name in self.pure_python_packages:
            self._copy_package(package_name, staging)
        (staging / "main.py").write_text(
            self._browser_launcher(config), encoding="utf-8"
        )
        return staging, metadata

    def build(self, target: str | Path) -> WebBuildResult:
        """Stage, package, normalize, validate, and manifest one target.

        Args:
            target: Repository-relative or absolute target directory.

        Returns:
            Normalized build result.

        Raises:
            FileNotFoundError: Pygbag does not produce expected static output.
        """
        resolved = self.resolve_target(target)
        staging, metadata = self.prepare(resolved)
        self.packager.build(staging)
        build_root = staging / "build" / "web"
        self._validate_build_output(build_root)
        output = self._normalize_output(build_root, metadata.slug)
        build_id = staging.name.rsplit("-", 1)[-1]
        manifest = self._update_manifest(metadata, build_id)
        return WebBuildResult(
            target=resolved,
            staging=staging,
            output=output,
            manifest=manifest,
            metadata=metadata,
            build_id=build_id,
        )

    def _load_target_config(
        self, target: Path
    ) -> tuple[dict[str, Any], WebShowcaseMetadata]:
        config = ConfigurationLoader.load_profile(target / "tatuy.yml", "web")
        raw_showcase = config.pop("showcase", {})
        if not isinstance(raw_showcase, dict):
            raise TypeError("showcase configuration must be a mapping")
        metadata = WebShowcaseMetadata.from_mapping(
            raw_showcase,
            default_slug=target.name,
        )
        return merge_config(config, self.runtime_overrides), metadata

    def _content_fingerprint(self, target: Path) -> str:
        digest = hashlib.sha256()
        roots = [("target", target), ("tatuy", self.tatuy_source)]
        roots.extend(
            (package_name, self._package_source(package_name))
            for package_name in self.pure_python_packages
        )
        for label, root in roots:
            for path in self._packaged_files(root):
                relative = path.relative_to(root).as_posix()
                digest.update(f"{label}/{relative}\0".encode("utf-8"))
                digest.update(path.read_bytes())
        return digest.hexdigest()[:8]

    @staticmethod
    def _packaged_files(root: Path) -> list[Path]:
        files: list[Path] = []
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or ".mypy_cache" in path.parts:
                continue
            if path.suffix in {".pyc", ".pyo"}:
                continue
            files.append(path)
        return sorted(files)

    def _copy_target(self, target: Path, staging: Path) -> None:
        for source in self._packaged_files(target):
            relative = source.relative_to(target)
            if relative.name in {"tatuy.yml", "tatuy.web.yml"}:
                continue
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    def _copy_tatuy(self, staging: Path) -> None:
        shutil.copytree(
            self.tatuy_source,
            staging / "tatuy",
            ignore=shutil.ignore_patterns(
                "__pycache__", ".mypy_cache", "*.pyc", "*.pyo"
            ),
        )

    @staticmethod
    def _package_source(package_name: str) -> Path:
        spec = importlib.util.find_spec(package_name)
        if spec is None or spec.submodule_search_locations is None:
            raise RuntimeError(f"Cannot resolve package {package_name!r}")
        return Path(next(iter(spec.submodule_search_locations)))

    def _copy_package(self, package_name: str, staging: Path) -> None:
        shutil.copytree(
            self._package_source(package_name),
            staging / package_name,
            ignore=shutil.ignore_patterns(
                "__pycache__", ".mypy_cache", "*.pyc", "*.pyo"
            ),
        )

    @staticmethod
    def _browser_launcher(config: Mapping[str, Any]) -> str:
        return f'''"""Generated Pygbag launcher for a Tatuy web target."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

# Pygbag discovers WASM package dependencies from top-level imports in main.py.
import pygame

from app import create_app
from tatuy.engine.runtime.host import AsyncRuntimeHost

PYGAME_PRELOAD = pygame
WEB_CONFIG = {dict(config)!r}


async def main() -> None:
    os.chdir(Path(__file__).resolve().parent)
    app = create_app(WEB_CONFIG)
    await AsyncRuntimeHost().run(app.build())


asyncio.run(main())
'''

    @staticmethod
    def _validate_build_output(build_root: Path) -> None:
        if not build_root.is_dir():
            raise FileNotFoundError(
                f"Pygbag static build not found at {build_root}"
            )
        if not (build_root / "index.html").is_file():
            raise FileNotFoundError(
                f"Pygbag build has no index.html: {build_root}"
            )

    def _normalize_output(self, build_root: Path, slug: str) -> Path:
        play_root = self.output_root / "play"
        target_root = play_root / slug
        if target_root.exists():
            shutil.rmtree(target_root)
        target_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(build_root, target_root)
        return target_root

    def _update_manifest(
        self,
        metadata: WebShowcaseMetadata,
        build_id: str,
    ) -> Path:
        self.output_root.mkdir(parents=True, exist_ok=True)
        manifest_path = self.output_root / "manifest.json"
        entries: list[dict[str, str]] = []
        if manifest_path.exists():
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            existing = payload.get("targets", [])
            if isinstance(existing, list):
                entries = [
                    entry for entry in existing if isinstance(entry, dict)
                ]
        current = {
            **metadata.to_dict(),
            "entrypoint": f"play/{metadata.slug}/index.html",
            "build_id": build_id,
        }
        entries = [
            entry for entry in entries if entry.get("slug") != metadata.slug
        ]
        entries.append(current)
        entries.sort(key=lambda entry: str(entry.get("slug", "")))
        manifest_path.write_text(
            json.dumps({"targets": entries}, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.output_root / ".nojekyll").touch()
        return manifest_path

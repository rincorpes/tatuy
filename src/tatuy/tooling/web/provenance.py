"""Build provenance recorded for published Tatuy browser targets."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


@dataclass(frozen=True, slots=True)
class WebBuildProvenance:
    """Identify the engine, bridge, source, and commit behind one web bundle."""

    build_id: str
    source: str
    commit_sha: str
    tatuy_version: str
    bridge: str
    bridge_version: str
    python_version: str

    @classmethod
    def current(
        cls,
        repository_root: Path,
        *,
        build_id: str,
        source: str,
    ) -> WebBuildProvenance:
        """Capture deterministic build metadata from the current checkout."""
        return cls(
            build_id=build_id,
            source=source,
            commit_sha=_commit_sha(repository_root),
            tatuy_version=_package_version("tatuy"),
            bridge="pygbag",
            bridge_version=_package_version("pygbag"),
            python_version=(
                f"{sys.version_info.major}.{sys.version_info.minor}."
                f"{sys.version_info.micro}"
            ),
        )

    def to_dict(self) -> dict[str, str]:
        """Return JSON-serializable provenance metadata."""
        return asdict(self)

    def write(self, path: Path) -> None:
        """Write deterministic JSON metadata beside a normalized web bundle."""
        path.write_text(
            json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


@dataclass(frozen=True, slots=True)
class WebSiteProvenance:
    """Record the toolchain and checkout that produced the composed site."""

    commit_sha: str
    tatuy_version: str
    python_version: str
    pygbag_version: str
    mkdocs_version: str
    poetry_lock_sha256: str

    @classmethod
    def current(cls, repository_root: Path) -> WebSiteProvenance:
        """Capture deterministic publication metadata for the current checkout."""
        lock = repository_root / "poetry.lock"
        lock_hash = (
            hashlib.sha256(lock.read_bytes()).hexdigest()
            if lock.is_file()
            else "missing"
        )
        return cls(
            commit_sha=_commit_sha(repository_root),
            tatuy_version=_package_version("tatuy"),
            python_version=(
                f"{sys.version_info.major}.{sys.version_info.minor}."
                f"{sys.version_info.micro}"
            ),
            pygbag_version=_package_version("pygbag"),
            mkdocs_version=_package_version("mkdocs"),
            poetry_lock_sha256=lock_hash,
        )

    def write(self, path: Path) -> None:
        """Write deterministic site provenance as JSON."""
        path.write_text(
            json.dumps(asdict(self), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def _package_version(package: str) -> str:
    try:
        return version(package)
    except PackageNotFoundError:
        return "unknown"


def _commit_sha(repository_root: Path) -> str:
    github_sha = os.environ.get("GITHUB_SHA", "").strip()
    if github_sha:
        return github_sha
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip() or "unknown"

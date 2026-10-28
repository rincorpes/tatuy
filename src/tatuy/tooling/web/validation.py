"""Validate static browser output for GitHub Project Pages deployment."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_HTML_URL_PATTERN = re.compile(r"(?:href|src|action)=[\"']([^\"']+)[\"']", re.IGNORECASE)
_CSS_URL_PATTERN = re.compile(r"url\(\s*[\"']?([^\"')]+)", re.IGNORECASE)
_EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "data:", "blob:", "#")


@dataclass(frozen=True, slots=True)
class BasePathViolation:
    """Describe one URL that would escape a GitHub Project Pages base path."""

    path: Path
    url: str


class WebOutputBasePathValidator:
    """Reject internal URLs that escape the configured Project Pages base path."""

    def __init__(self, project_base_path: str = "/tatuy/") -> None:
        """Configure the GitHub Project Pages path allowed for root URLs.

        Args:
            project_base_path: Repository subpath served by GitHub Pages.
        """
        normalized = f"/{project_base_path.strip('/')}/"
        self._project_base_path = normalized
        self._project_root = normalized.rstrip("/")

    def validate(self, output_root: Path) -> None:
        """Validate HTML and CSS references beneath ``output_root``.

        Args:
            output_root: Generated static-site root.

        Raises:
            ValueError: One or more internal URLs start at the domain root.
        """
        violations = self.find_violations(output_root)
        if not violations:
            return
        details = ", ".join(
            f"{violation.path.as_posix()}: {violation.url}"
            for violation in violations
        )
        raise ValueError(
            "Web output contains root-absolute URLs that are unsafe for "
            f"GitHub Project Pages: {details}"
        )

    def find_violations(self, output_root: Path) -> tuple[BasePathViolation, ...]:
        """Return root-absolute internal URL references beneath ``output_root``."""
        root = output_root.resolve()
        violations: list[BasePathViolation] = []
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".html", ".css"}:
                continue
            text = path.read_text(encoding="utf-8")
            pattern = _CSS_URL_PATTERN if path.suffix.lower() == ".css" else _HTML_URL_PATTERN
            for match in pattern.finditer(text):
                url = match.group(1).strip()
                if self._is_root_absolute_internal(url):
                    violations.append(
                        BasePathViolation(path=path.relative_to(root), url=url)
                    )
        return tuple(violations)

    def _is_root_absolute_internal(self, url: str) -> bool:
        if not url or url.startswith(_EXTERNAL_PREFIXES):
            return False
        if not url.startswith("/"):
            return False
        return not (
            url == self._project_root
            or url.startswith(self._project_base_path)
        )


class WebOutputStructureValidator:
    """Validate the publication structure described by the showcase manifest."""

    _required_files = (
        Path("index.html"),
        Path("docs/index.html"),
        Path("manifest.json"),
        Path("build.json"),
        Path(".nojekyll"),
    )
    _forbidden_parts = {
        ".tatuy",
        ".venv",
        ".vscode",
        "recordings",
        "replays",
        "screenshots",
        "venv",
    }
    _forbidden_names = {
        ".env",
        "tatuy.local.yml",
        "tatuy.local.yaml",
        "tatuy.local.toml",
    }
    _forbidden_suffixes = {".key", ".pem"}

    def validate(self, output_root: Path) -> None:
        """Require publication roots and every declared playable bundle.

        Args:
            output_root: Generated static-site root.

        Raises:
            FileNotFoundError: Required output or referenced assets are missing.
            TypeError: The generated manifest has an invalid shape.
            ValueError: The manifest contains duplicate slugs or invalid entries.
        """
        root = output_root.resolve()
        missing = [path for path in self._required_files if not (root / path).is_file()]
        if missing:
            joined = ", ".join(path.as_posix() for path in missing)
            raise FileNotFoundError(f"Required web output is missing: {joined}")

        self._validate_no_private_paths(root)
        manifest = self._load_manifest(root / "manifest.json")
        targets = manifest.get("targets")
        if not isinstance(targets, list):
            raise TypeError("Showcase manifest targets must be a list")

        slugs: set[str] = set()
        for target in targets:
            if not isinstance(target, dict):
                raise TypeError("Showcase manifest target must be a mapping")
            slug = self._required_string(target, "slug")
            if slug in slugs:
                raise ValueError(f"Duplicate showcase slug in manifest: {slug}")
            slugs.add(slug)

            if target.get("web") is True:
                if target.get("playable") is not True:
                    raise ValueError(f"Browser target is not marked playable: {slug}")
                entrypoint = self._required_string(target, "entrypoint")
                self._require_relative_file(root, entrypoint, label=f"bundle for {slug}")
                self._require_relative_file(
                    root,
                    f"play/{slug}/build.json",
                    label=f"provenance for {slug}",
                )

            screenshot = target.get("screenshot")
            if screenshot is not None:
                if not isinstance(screenshot, str) or not screenshot.strip():
                    raise TypeError(f"Showcase screenshot must be a non-empty string: {slug}")
                self._require_relative_file(root, screenshot, label=f"screenshot for {slug}")

    def _validate_no_private_paths(self, root: Path) -> None:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            lower_parts = {part.lower() for part in relative.parts}
            name = path.name.lower()
            if lower_parts & self._forbidden_parts:
                raise ValueError(
                    f"Private/local path leaked into web output: {relative.as_posix()}"
                )
            if name in self._forbidden_names or name.startswith(".env."):
                raise ValueError(
                    f"Private/local file leaked into web output: {relative.as_posix()}"
                )
            if path.suffix.lower() in self._forbidden_suffixes:
                raise ValueError(
                    f"Key material leaked into web output: {relative.as_posix()}"
                )

    @staticmethod
    def _load_manifest(path: Path) -> dict[str, Any]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise TypeError("Showcase manifest must be a mapping")
        return payload

    @staticmethod
    def _required_string(mapping: dict[str, Any], key: str) -> str:
        value = mapping.get(key)
        if not isinstance(value, str) or not value.strip():
            raise TypeError(f"Showcase manifest {key} must be a non-empty string")
        return value.strip()

    @staticmethod
    def _require_relative_file(root: Path, value: str, *, label: str) -> None:
        relative = Path(value)
        if relative.is_absolute():
            raise ValueError(f"Showcase {label} must be relative: {value}")
        resolved = (root / relative).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"Showcase {label} escapes web output: {value}") from exc
        if not resolved.is_file():
            raise FileNotFoundError(f"Showcase {label} not found: {resolved}")

"""Validate static browser output for GitHub Project Pages deployment."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

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

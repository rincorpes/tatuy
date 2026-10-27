"""Data models used by Tatuy web-target packaging tooling."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class WebShowcaseMetadata:
    """Describe one browser-playable Tatuy target in the showcase manifest.

    Attributes:
        slug: URL-safe output directory name used beneath ``play/``.
        title: Human-readable target title.
        description: Optional short showcase description.
    """

    slug: str
    title: str
    description: str = ""

    @classmethod
    def from_mapping(
        cls,
        mapping: Mapping[str, Any],
        *,
        default_slug: str,
    ) -> WebShowcaseMetadata:
        """Build metadata from optional configuration values.

        Args:
            mapping: Optional ``showcase`` configuration mapping.
            default_slug: Slug inferred from the target directory.

        Returns:
            Validated showcase metadata with deterministic defaults.

        Raises:
            TypeError: A metadata field has the wrong type.
            ValueError: The resolved slug is empty or not URL-safe.
        """
        slug = mapping.get("slug", default_slug)
        title = mapping.get("title", default_slug.replace("_", " ").title())
        description = mapping.get("description", "")
        if not isinstance(slug, str):
            raise TypeError("showcase.slug must be a string")
        if not isinstance(title, str):
            raise TypeError("showcase.title must be a string")
        if not isinstance(description, str):
            raise TypeError("showcase.description must be a string")
        normalized_slug = slug.strip()
        if not normalized_slug:
            raise ValueError("showcase.slug cannot be empty")
        if any(
            character not in "abcdefghijklmnopqrstuvwxyz0123456789-_"
            for character in normalized_slug
        ):
            raise ValueError(
                "showcase.slug may contain only lowercase letters, numbers, '-' and '_'"
            )
        return cls(
            slug=normalized_slug,
            title=title.strip() or normalized_slug,
            description=description.strip(),
        )

    def to_dict(self) -> dict[str, str]:
        """Return JSON-serializable metadata."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class WebBuildResult:
    """Describe the normalized output produced for one Tatuy web target.

    Attributes:
        target: Resolved source target directory.
        staging: Content-addressed staging directory used by Pygbag.
        output: Normalized static output directory under ``play/<slug>``.
        manifest: Showcase manifest path updated by the build.
        metadata: Resolved showcase metadata.
        build_id: Content fingerprint identifying this staged build.
    """

    target: Path
    staging: Path
    output: Path
    manifest: Path
    metadata: WebShowcaseMetadata
    build_id: str

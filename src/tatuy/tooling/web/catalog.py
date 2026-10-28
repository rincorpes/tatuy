"""Discover and validate showcase metadata for Tatuy web targets."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from tatuy.configuration import ConfigurationLoader


@dataclass(frozen=True, slots=True)
class ShowcaseCatalogEntry:
    """Describe one validated target in the public showcase catalog.

    Attributes:
        id: Stable catalog identifier independent from the generated URL.
        slug: URL-safe name used by playable and showcase output directories.
        title: Human-readable target title.
        description: Short public description.
        category: High-level catalog category such as ``fundamental``.
        tags: Search/filter tags attached to the target.
        source: Repository-relative source directory.
        docs: Optional repository-relative related documentation path.
        web: Whether the target declares browser support.
        playable: Whether a validated browser bundle is available.
        url: Human-facing showcase page relative to the web root.
        entrypoint: Raw runtime entrypoint relative to the web root.
    """

    id: str
    slug: str
    title: str
    description: str
    category: str
    tags: tuple[str, ...]
    source: str
    docs: str | None
    web: bool
    playable: bool
    url: str
    entrypoint: str
    build_id: str | None = None
    commit_sha: str | None = None
    tatuy_version: str | None = None
    bridge: str | None = None
    bridge_version: str | None = None
    python_version: str | None = None
    screenshot: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable catalog metadata.

        Returns:
            Dictionary suitable for the generated showcase manifest.
        """
        payload = asdict(self)
        payload["tags"] = list(self.tags)
        return payload


class ShowcaseCatalogBuilder:
    """Discover declared showcase targets and generate a validated manifest.

    Args:
        repository_root: Tatuy repository root containing source targets.
        targets_root: Root searched recursively for ``tatuy.web.yml`` files.
        output_root: Existing static web output containing playable bundles.
    """

    def __init__(
        self,
        repository_root: Path,
        *,
        targets_root: Path | None = None,
        output_root: Path | None = None,
    ) -> None:
        self.repository_root = repository_root.resolve()
        self.targets_root = (
            targets_root or self.repository_root / "examples"
        ).resolve()
        self.output_root = (
            output_root or self.repository_root / "build" / "web"
        ).resolve()

    def discover(
        self, *, require_playable_bundles: bool = True
    ) -> list[ShowcaseCatalogEntry]:
        """Discover and validate all declared showcase targets.

        Args:
            require_playable_bundles: Whether ``web: true`` targets must already
                have generated browser bundles beneath ``build/web/play``.

        Returns:
            Catalog entries sorted by stable target ID.

        Raises:
            FileNotFoundError: A declared source, docs path, or browser bundle is
                missing.
            TypeError: A required metadata value has the wrong type.
            ValueError: Metadata is incomplete or duplicate IDs/slugs exist.
        """
        if not self.targets_root.is_dir():
            raise FileNotFoundError(
                f"Showcase target root not found: {self.targets_root}"
            )

        entries: list[ShowcaseCatalogEntry] = []
        ids: set[str] = set()
        slugs: set[str] = set()
        for profile in sorted(self.targets_root.rglob("tatuy.web.yml")):
            target = profile.parent
            config = ConfigurationLoader.load_profile(target / "tatuy.yml", "web")
            showcase = config.get("showcase")
            if showcase is None:
                continue
            if not isinstance(showcase, dict):
                raise TypeError(
                    f"showcase metadata must be a mapping: {profile}"
                )
            entry = self._entry_from_mapping(
                showcase,
                profile=profile,
                require_playable_bundle=require_playable_bundles,
            )
            if entry.id in ids:
                raise ValueError(f"Duplicate showcase id: {entry.id}")
            if entry.slug in slugs:
                raise ValueError(f"Duplicate showcase slug: {entry.slug}")
            ids.add(entry.id)
            slugs.add(entry.slug)
            entries.append(entry)
        return sorted(entries, key=lambda entry: entry.id)

    def build(self) -> Path:
        """Generate the deterministic showcase catalog manifest.

        Returns:
            Path to ``build/web/manifest.json``.
        """
        entries = self.discover()
        self.output_root.mkdir(parents=True, exist_ok=True)
        manifest = self.output_root / "manifest.json"
        manifest.write_text(
            json.dumps(
                {"targets": [entry.to_dict() for entry in entries]},
                indent=2,
                sort_keys=False,
            )
            + "\n",
            encoding="utf-8",
        )
        (self.output_root / ".nojekyll").touch()
        return manifest

    def _entry_from_mapping(
        self,
        mapping: Mapping[str, Any],
        *,
        profile: Path,
        require_playable_bundle: bool,
    ) -> ShowcaseCatalogEntry:
        target_id = self._required_string(mapping, "id", profile)
        slug = self._required_string(mapping, "slug", profile)
        title = self._required_string(mapping, "title", profile)
        description = self._required_string(mapping, "description", profile)
        category = self._required_string(mapping, "category", profile)
        source = self._required_string(mapping, "source", profile)
        web = mapping.get("web", False)
        if not isinstance(web, bool):
            raise TypeError(f"showcase.web must be a boolean: {profile}")

        tags_value = mapping.get("tags", [])
        if not isinstance(tags_value, list) or not all(
            isinstance(tag, str) and tag.strip() for tag in tags_value
        ):
            raise TypeError(
                f"showcase.tags must be a list of non-empty strings: {profile}"
            )
        tags = tuple(dict.fromkeys(tag.strip() for tag in tags_value))

        docs_value = mapping.get("docs")
        if docs_value is not None and not isinstance(docs_value, str):
            raise TypeError(f"showcase.docs must be a string: {profile}")
        docs = docs_value.strip() if isinstance(docs_value, str) else None
        if docs == "":
            docs = None

        self._validate_slug(slug, profile)
        self._validate_repository_path(source, kind="source", profile=profile)
        source_path = self.repository_root / source
        if not source_path.is_dir() or not (source_path / "app.py").is_file():
            raise FileNotFoundError(
                f"Showcase source must contain app.py: {source_path}"
            )
        if source_path.resolve() != profile.parent.resolve():
            raise ValueError(
                f"showcase.source does not match its profile directory: {profile}"
            )

        if docs is not None:
            self._validate_repository_path(docs, kind="docs", profile=profile)
            docs_path = self.repository_root / docs
            if not docs_path.is_file():
                raise FileNotFoundError(
                    f"Showcase related docs not found: {docs_path}"
                )

        entrypoint = f"play/{slug}/index.html"
        playable = False
        provenance: dict[str, str | None] = {
            "build_id": None,
            "commit_sha": None,
            "tatuy_version": None,
            "bridge": None,
            "bridge_version": None,
            "python_version": None,
        }
        if web:
            bundle = self.output_root / entrypoint
            if require_playable_bundle and not bundle.is_file():
                raise FileNotFoundError(
                    f"Web showcase bundle not found for {target_id}: {bundle}"
                )
            playable = bundle.is_file()
            if playable:
                provenance = self._load_build_provenance(
                    slug,
                    require=require_playable_bundle,
                )

        screenshot_path = self.output_root / "assets" / "thumbnails" / f"{slug}.png"
        screenshot = (
            f"assets/thumbnails/{slug}.png" if screenshot_path.is_file() else None
        )

        return ShowcaseCatalogEntry(
            id=target_id,
            slug=slug,
            title=title,
            description=description,
            category=category,
            tags=tags,
            source=source,
            docs=docs,
            web=web,
            playable=playable,
            url=f"showcase/{slug}/",
            entrypoint=entrypoint,
            screenshot=screenshot,
            **provenance,
        )

    def _load_build_provenance(
        self,
        slug: str,
        *,
        require: bool,
    ) -> dict[str, str | None]:
        """Read normalized bundle provenance generated by ``WebTargetBuilder``."""
        path = self.output_root / "play" / slug / "build.json"
        if not path.is_file():
            if require:
                raise FileNotFoundError(
                    f"Web showcase provenance not found for {slug}: {path}"
                )
            return {
                "build_id": None,
                "commit_sha": None,
                "tatuy_version": None,
                "bridge": None,
                "bridge_version": None,
                "python_version": None,
            }
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise TypeError(f"Web showcase provenance must be a mapping: {path}")
        required = (
            "build_id",
            "commit_sha",
            "tatuy_version",
            "bridge",
            "bridge_version",
            "python_version",
        )
        result: dict[str, str | None] = {}
        for key in required:
            value = payload.get(key)
            if not isinstance(value, str) or not value.strip():
                raise TypeError(
                    f"Web showcase provenance {key} must be a non-empty string: {path}"
                )
            result[key] = value.strip()
        return result

    def _validate_repository_path(
        self,
        value: str,
        *,
        kind: str,
        profile: Path,
    ) -> None:
        path = Path(value)
        if path.is_absolute():
            raise ValueError(
                f"showcase.{kind} must be repository-relative: {profile}"
            )
        resolved = (self.repository_root / path).resolve()
        try:
            resolved.relative_to(self.repository_root)
        except ValueError as exc:
            raise ValueError(
                f"showcase.{kind} escapes the repository: {profile}"
            ) from exc

    @staticmethod
    def _required_string(
        mapping: Mapping[str, Any],
        key: str,
        profile: Path,
    ) -> str:
        value = mapping.get(key)
        if not isinstance(value, str):
            raise TypeError(f"showcase.{key} must be a string: {profile}")
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"showcase.{key} cannot be empty: {profile}")
        return normalized

    @staticmethod
    def _validate_slug(slug: str, profile: Path) -> None:
        if any(
            character not in "abcdefghijklmnopqrstuvwxyz0123456789-_"
            for character in slug
        ):
            raise ValueError(
                "showcase.slug may contain only lowercase letters, numbers, "
                f"'-' and '_': {profile}"
            )

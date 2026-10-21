from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ProjectEntry:
    key: str
    name: str
    kind: str
    path: Path


def discover_projects(
    *,
    engine_root: Path,
    projects_root: Path,
) -> list[ProjectEntry]:
    engine_root = engine_root.resolve()
    projects_root = projects_root.resolve()

    entries = [
        ProjectEntry(
            key="engine",
            name="engine",
            kind="engine",
            path=engine_root,
        )
    ]

    entries.extend(
        _discover_standalone_projects(
            engine_root=engine_root,
            projects_root=projects_root,
        )
    )

    entries.extend(
        _discover_example_targets(
            engine_root / "examples" / "experiments",
            kind="experiment",
        )
    )

    entries.extend(
        _discover_example_targets(
            engine_root / "examples" / "games",
            kind="game",
        )
    )

    return entries


def _discover_standalone_projects(
    *,
    engine_root: Path,
    projects_root: Path,
) -> list[ProjectEntry]:
    if not projects_root.is_dir():
        return []

    entries: list[ProjectEntry] = []

    for directory in sorted(
        projects_root.iterdir(),
        key=lambda item: item.name.casefold(),
    ):
        if not directory.is_dir() or directory.is_symlink():
            continue

        resolved = directory.resolve()

        if resolved == engine_root:
            continue

        manifest = resolved / "tatuy.toml"

        if not manifest.is_file():
            continue

        entries.append(
            ProjectEntry(
                key=f"project:{directory.name}",
                name=directory.name,
                kind="project",
                path=resolved,
            )
        )

    return entries


def _discover_example_targets(
    root: Path,
    *,
    kind: str,
) -> list[ProjectEntry]:
    if not root.is_dir():
        return []

    entries: list[ProjectEntry] = []

    _walk_example_targets(
        root,
        kind=kind,
        logical_prefix="",
        entries=entries,
    )

    return entries


def _walk_example_targets(
    directory: Path,
    *,
    kind: str,
    logical_prefix: str,
    entries: list[ProjectEntry],
) -> None:
    for child in sorted(
        directory.iterdir(),
        key=lambda item: item.name.casefold(),
    ):
        if not child.is_dir() or child.is_symlink():
            continue

        logical_name = _logical_directory_name(child.name)

        if logical_name is None:
            continue

        logical_path = (
            f"{logical_prefix}.{logical_name}"
            if logical_prefix
            else logical_name
        )

        if (child / "app.py").is_file():
            entries.append(
                ProjectEntry(
                    key=f"{kind}:{logical_path}",
                    name=logical_path,
                    kind=kind,
                    path=child.resolve(),
                )
            )

        _walk_example_targets(
            child,
            kind=kind,
            logical_prefix=logical_path,
            entries=entries,
        )


def _logical_directory_name(
    directory_name: str,
) -> str | None:
    number, separator, name = directory_name.partition("_")

    if not separator or not number.isdigit():
        return None

    if not name.isidentifier() or name.startswith("_"):
        return None

    return name

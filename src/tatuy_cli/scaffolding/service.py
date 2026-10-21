from __future__ import annotations

import os
import re
import shutil
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path
from typing import cast

from tatuy_cli.scaffolding.model import (
    CreatedTarget,
    CreateTargetRequest,
    TatuySource,
)
from tatuy_cli.scaffolding.templates import (
    render_app,
    render_gitignore,
    render_manifest,
    render_pyproject,
    render_readme,
)


TARGET_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

CATEGORY_ROOTS = {
    "experiment": "experiments",
    "game": "games",
}


class TargetScaffolder:
    def __init__(
        self,
        *,
        engine_root: Path,
        projects_root: Path | None = None,
        restrict_projects_to_root: bool = False,
    ) -> None:
        self.engine_root = engine_root.resolve()
        self.projects_root = (
            projects_root.resolve()
            if projects_root is not None
            else self.engine_root.parent.resolve()
        )
        self.restrict_projects_to_root = restrict_projects_to_root

    def create(self, request: CreateTargetRequest) -> CreatedTarget:
        self._validate_request(request)

        source = self._resolve_tatuy_source(request)
        destination = self._resolve_destination(request)

        if destination.exists():
            raise ValueError(f"Target already exists: {destination}")

        title = self._title(request.name)

        status = "idea" if request.kind == "experiment" else "active"

        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

        tatuy_path = None
        tatuy_version = None

        if source == "local":
            tatuy_path = self._relative_engine_path(destination)

        elif source == "pypi":
            tatuy_version = (
                request.tatuy_version or self._current_tatuy_version()
            )

        run_command = self._run_command(request)

        try:
            destination.mkdir(parents=True)
            (destination / "assets").mkdir()

            self._write(
                destination / "app.py",
                render_app(),
            )

            self._write(
                destination / "README.md",
                render_readme(
                    title=title,
                    description=request.description,
                    run_command=run_command,
                    standalone=request.kind == "project",
                ),
            )

            manifest_path = destination / "tatuy.toml"

            self._write(
                manifest_path,
                render_manifest(
                    name=request.name,
                    title=title,
                    kind=request.kind,
                    description=request.description,
                    status=status,
                    created_at=created_at,
                    tags=request.tags,
                    tatuy_source=source,
                    tatuy_path=tatuy_path,
                    tatuy_version=tatuy_version,
                ),
            )

            if request.kind == "project":
                self._write(
                    destination / "pyproject.toml",
                    render_pyproject(
                        name=request.name,
                        description=request.description,
                        tatuy_source=source,
                        tatuy_path=tatuy_path,
                        tatuy_version=tatuy_version,
                    ),
                )

                self._write(
                    destination / ".gitignore",
                    render_gitignore(),
                )

        except Exception:
            if destination.exists():
                shutil.rmtree(destination)

            raise

        return CreatedTarget(
            kind=request.kind,
            name=request.name,
            path=destination,
            manifest_path=manifest_path,
            run_command=run_command,
        )

    def _validate_request(
        self,
        request: CreateTargetRequest,
    ) -> None:
        if request.kind not in {
            "experiment",
            "game",
            "project",
        }:
            raise ValueError(f"Unknown target kind: {request.kind}")

        if not TARGET_NAME_PATTERN.fullmatch(request.name):
            raise ValueError(
                "Target names must use lowercase snake_case, "
                "for example procedural_fire."
            )

        if request.kind != "project":
            if request.destination is not None:
                raise ValueError(
                    "Only standalone projects accept a destination."
                )

            if request.tatuy_source not in {
                None,
                "workspace",
            }:
                raise ValueError(
                    "Experiments and games always use the "
                    "Tatuy workspace source."
                )

    def _resolve_tatuy_source(
        self,
        request: CreateTargetRequest,
    ) -> TatuySource:
        if request.kind in {"experiment", "game"}:
            return "workspace"

        source = request.tatuy_source or "local"

        if source not in {"local", "pypi"}:
            raise ValueError(
                "Standalone projects must use either "
                "'local' or 'pypi' as their Tatuy source."
            )

        return cast(TatuySource, source)

    def _resolve_destination(
        self,
        request: CreateTargetRequest,
    ) -> Path:
        if request.kind in CATEGORY_ROOTS:
            root = self.engine_root / "examples" / CATEGORY_ROOTS[request.kind]

            if not root.is_dir():
                raise ValueError(f"Missing target directory: {root}")

            number = self._next_number(root)

            return (root / f"{number:03d}_{request.name}").resolve()

        if request.destination is not None:
            destination = request.destination

            if not destination.is_absolute():
                destination = Path.cwd() / destination
        else:
            destination = self.projects_root / request.name

        destination = destination.resolve()

        if self.restrict_projects_to_root:
            root = self.projects_root.resolve()

            if not root.is_dir():
                raise ValueError(f"Projects root does not exist: {root}")

            if not destination.is_relative_to(root):
                raise ValueError(
                    "Project destination must remain inside "
                    "the configured projects root."
                )

        return destination

    @staticmethod
    def _next_number(root: Path) -> int:
        numbers: list[int] = []

        for child in root.iterdir():
            if not child.is_dir():
                continue

            prefix, separator, _ = child.name.partition("_")

            if separator and prefix.isdigit():
                numbers.append(int(prefix))

        return max(numbers, default=0) + 1

    def _relative_engine_path(
        self,
        destination: Path,
    ) -> str:
        try:
            relative = os.path.relpath(
                self.engine_root,
                destination,
            )
        except ValueError as exc:
            raise ValueError(
                "Local Tatuy projects must be on the same "
                "filesystem drive as the engine repository."
            ) from exc

        return Path(relative).as_posix()

    def _current_tatuy_version(self) -> str:
        try:
            return package_version("tatuy")
        except PackageNotFoundError:
            pass

        pyproject = self.engine_root / "pyproject.toml"

        if pyproject.is_file():
            pattern = re.compile(r'^version\s*=\s*["\']([^"\']+)["\']')

            for line in pyproject.read_text(encoding="utf-8").splitlines():
                match = pattern.match(line.strip())

                if match:
                    return match.group(1)

        raise ValueError(
            "Could not determine the Tatuy version. "
            "Provide --tatuy-version explicitly."
        )

    @staticmethod
    def _title(name: str) -> str:
        return name.replace("_", " ").title()

    @staticmethod
    def _run_command(
        request: CreateTargetRequest,
    ) -> str:
        if request.kind == "experiment":
            return (
                "poetry run python manage.py " f"run experiment {request.name}"
            )

        if request.kind == "game":
            return "poetry run python manage.py " f"run game {request.name}"

        return "poetry run python app.py"

    @staticmethod
    def _write(path: Path, content: str) -> None:
        path.write_text(
            content,
            encoding="utf-8",
        )

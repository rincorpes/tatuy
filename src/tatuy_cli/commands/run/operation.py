from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

from tatuy_cli.commands.run.input import RunTargetInput

CATEGORY_ROOTS = {
    "example": "fundamentals",
    "experiment": "experiments",
    "game": "games",
}


class TargetResolutionError(ValueError):
    """A requested runnable target cannot be resolved unambiguously."""


class TargetResolver:
    """Resolve logical names while preserving numbered import paths."""

    def __init__(self, root: Path):
        self.root = root

    @staticmethod
    def _children(
        parent: Path, *, allow_unnumbered: bool = False
    ) -> dict[str, Path]:
        children: dict[str, Path] = {}
        if not parent.is_dir():
            raise TargetResolutionError(f"Directory does not exist: {parent}")

        for directory in sorted(parent.iterdir()):
            if not directory.is_dir() or directory.is_symlink():
                continue

            number, separator, name = directory.name.partition("_")
            if not separator or not number.isdigit():
                if not allow_unnumbered:
                    continue
                name = directory.name

            if not name.isidentifier() or name.startswith("_"):
                continue

            if name in children:
                raise TargetResolutionError(
                    f"Duplicate target name '{name}' in {parent}: "
                    f"{children[name].name}, {directory.name}"
                )
            children[name] = directory

        return children

    def _targets(self, directory: Path, prefix: str) -> list[str]:
        targets = [prefix] if (directory / "app.py").is_file() else []
        for name, child in self._children(directory).items():
            targets.extend(self._targets(child, f"{prefix}.{name}"))
        return targets

    def resolve(self, category: str, name: str) -> Path:
        parts = name.split(".")
        if any(
            not part.isidentifier() or part.startswith("_") for part in parts
        ):
            raise TargetResolutionError(
                f"Invalid target '{name}'. Use dotted names without numeric "
                "prefixes, for example movement.platformer."
            )
        print(parts)
        root_name = CATEGORY_ROOTS[category]
        categories = self._children(self.root, allow_unnumbered=True)
        directory = categories.get(root_name)
        if directory is None:
            raise TargetResolutionError(
                f"Missing '{root_name}' directory in {self.root}. "
                f"Create '{root_name}' or a numbered version such as "
                f"'001_{root_name}'."
            )

        for index, part in enumerate(parts):
            children = self._children(directory)
            child = children.get(part)
            if child is None:
                prefix = ".".join(parts[:index])
                choices = [
                    f"{prefix}.{key}" if prefix else key for key in children
                ]
                available = ", ".join(choices) or "(none)"
                raise TargetResolutionError(
                    f"Unknown {category} '{name}'. "
                    f"Available under {prefix or root_name}: {available}"
                )
            directory = child

        if not (directory / "app.py").is_file():
            targets = self._targets(directory, name)
            if targets:
                raise TargetResolutionError(
                    f"'{name}' is a group. Available targets: "
                    + ", ".join(targets)
                )
            raise TargetResolutionError(
                f"{directory} has no app.py or runnable numbered descendants."
            )

        return directory


class RunTargetOperation:
    def execute(self, input_data: RunTargetInput):
        try:
            directory = TargetResolver(input_data.examples_path).resolve(
                input_data.category, input_data.name
            )
        except TargetResolutionError as error:
            print(error, file=sys.stderr)
            return 1

        relative_path = directory.relative_to(input_data.examples_path)
        module_name = ".".join(("examples", *relative_path.parts, "app"))
        module = import_module(module_name)
        entrypoint = getattr(module, "main", None)

        if not callable(entrypoint):
            print(
                f"{directory / 'app.py'} must define a callable main().",
                file=sys.stderr,
            )
            return 1

        return entrypoint() or 0

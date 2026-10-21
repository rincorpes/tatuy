from __future__ import annotations

from limen.argument_type import ArgumentType
from limen.base_command import BaseCommand
from limen.registry import CommandRegistry

from tatuy_cli.commands.create.input import CreateTargetInput
from tatuy_cli.commands.create.operation import CreateTargetOperation


@CommandRegistry.implementation("create")
class CreateCommand(BaseCommand):
    is_group = True

    summary = (
        "Create a Tatuy experiment, reference game, " "or standalone project."
    )


class BaseCreateCommand(BaseCommand):
    abstract = True
    parent = "create"

    kind: str

    input_class = CreateTargetInput
    operation_class = CreateTargetOperation

    args = [
        ArgumentType(
            name="name",
            data_type=str,
            required=True,
            help_text=("Logical lowercase snake_case target name."),
        ),
        ArgumentType(
            name="description",
            data_type=str,
            required=False,
            help_text="Describe the purpose or idea.",
        ),
        ArgumentType(
            name="tags",
            data_type=str,
            required=False,
            help_text=("Comma-separated metadata tags."),
        ),
        ArgumentType(
            name="path",
            data_type=str,
            required=False,
            help_text=("Destination for standalone projects."),
        ),
        ArgumentType(
            name="tatuy_source",
            data_type=str,
            required=False,
            help_text=("Tatuy source for projects: local or pypi."),
        ),
        ArgumentType(
            name="tatuy_version",
            data_type=str,
            required=False,
            help_text=("Tatuy PyPI version for standalone projects."),
        ),
    ]

    def build_input(self, **kwargs):
        tags = tuple(
            tag.strip()
            for tag in (kwargs.get("tags") or "").split(",")
            if tag.strip()
        )

        return self.input_class(
            kind=self.kind,
            name=kwargs["name"],
            description=kwargs.get("description") or "",
            tags=tags,
            path=kwargs.get("path"),
            tatuy_source=kwargs.get("tatuy_source"),
            tatuy_version=kwargs.get("tatuy_version"),
        )


@CommandRegistry.implementation("create.experiment")
class CreateExperimentCommand(BaseCreateCommand):
    abstract = False
    name = "experiment"
    kind = "experiment"

    summary = "Create a gameplay experiment."


@CommandRegistry.implementation("create.game")
class CreateGameCommand(BaseCreateCommand):
    abstract = False
    name = "game"
    kind = "game"

    summary = "Create a Tatuy reference game or clone."


@CommandRegistry.implementation("create.project")
class CreateProjectCommand(BaseCreateCommand):
    abstract = False
    name = "project"
    kind = "project"

    summary = "Create a standalone project using Tatuy."

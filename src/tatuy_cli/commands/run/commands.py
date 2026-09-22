from __future__ import annotations

from limen.argument_type import ArgumentType
from limen.base_command import BaseCommand
from limen.registry import CommandRegistry

from tatuy_cli.commands.run.input import RunTargetInput
from tatuy_cli.commands.run.operation import RunTargetOperation


@CommandRegistry.implementation("run")
class RunCommand(BaseCommand):

    is_group = True
    summary = "Run a fundamental example, gameplay experiment, or game."


class BaseRunCommand(BaseCommand):

    abstract = True
    parent = "run"
    category: str
    input_class = RunTargetInput
    operation_class = RunTargetOperation
    args = [
        ArgumentType(
            name="name",
            data_type=str,
            required=True,
            help_text=(
                "Logical target name without numeric prefixes; "
                "use dots for nested folders (movement.platformer)."
            ),
        ),
    ]

    def build_input(self, **kwargs):
        return self.input_class(name=kwargs["name"], category=self.category)


@CommandRegistry.implementation("example")
class RunExampleCommand(BaseRunCommand):
    abstract = False
    name = "example"
    category = "example"
    summary = "Run an example from examples/fundamentals."


@CommandRegistry.implementation("experiment")
class RunExperimentCommand(BaseRunCommand):
    abstract = False
    name = "experiment"
    category = "experiment"
    summary = "Run a gameplay experiment from examples/experiments."


@CommandRegistry.implementation("game")
class RunGameCommand(BaseRunCommand):
    abstract = False
    name = "game"
    category = "game"
    summary = "Run a reference game from examples/games."

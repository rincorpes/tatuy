from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, version

from limen.app import BaseCLIApp
from limen.config import CLIConfig
from limen.runner import run_cli

from tatuy_cli.commands.run.commands import BaseRunCommand

from . import commands  # pylint: disable=unused-import


class TatuyCLI(BaseCLIApp):

    def __init__(self, config: CLIConfig) -> None:
        super().__init__(config)
        self.build_commands()

    def define_command_arguments(self, command_parser, command_cls) -> None:
        # Limen normally exposes ArgumentType values as --options. These
        # run commands instead accept a required positional target name.
        if issubclass(command_cls, BaseRunCommand):
            for argument in command_cls.define_arguments():
                command_parser.add_argument(
                    argument.name,
                    type=argument.data_type,
                    help=argument.help_text,
                )
            return
        super().define_command_arguments(command_parser, command_cls)


def create_config(
    global_parser: argparse.ArgumentParser,
) -> CLIConfig:
    return CLIConfig(
        app_name="tatuy-cli",
        description="Run Tatuy examples, experiments, and games.",
        usage="%(prog)s [options] <command> [<args>]",
        formatter_class=global_parser.formatter_class,
        parents=[global_parser],
    )


def package_version() -> str:
    try:
        return version("tatuy")
    except PackageNotFoundError:
        return "0.0.0"


def main(argv: list[str] | None = None) -> int:
    return run_cli(
        version=package_version(),
        app_factory=TatuyCLI,
        config_factory=create_config,
        argv=argv,
    )


if __name__ == "__main__":
    raise SystemExit(main())

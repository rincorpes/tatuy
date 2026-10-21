"""Check nested CLI commands that reuse names under different parents."""

import pytest

from tatuy_cli.app import main
from tatuy_cli.commands.create.operation import CreateTargetOperation
from tatuy_cli.commands.run.operation import RunTargetOperation


@pytest.mark.parametrize("kind", ["experiment", "game", "project"])
def test_create_command_dispatches_with_description(monkeypatch, kind):
    received = []

    def execute(self, input_data):
        received.append(input_data)
        return 0

    monkeypatch.setattr(CreateTargetOperation, "execute", execute)

    assert main([
        "create", kind, "asteroids",
        "--description", "Tatuy implementation of Asteroids.",
    ]) == 0
    assert len(received) == 1
    assert received[0].kind == kind
    assert received[0].name == "asteroids"
    assert received[0].description == "Tatuy implementation of Asteroids."


@pytest.mark.parametrize("category", ["example", "experiment", "game"])
def test_run_command_dispatches_to_run_operation(monkeypatch, category):
    received = []

    def execute(self, input_data):
        received.append(input_data)
        return 0

    monkeypatch.setattr(RunTargetOperation, "execute", execute)

    assert main(["run", category, "asteroids"]) == 0
    assert len(received) == 1
    assert received[0].category == category
    assert received[0].name == "asteroids"

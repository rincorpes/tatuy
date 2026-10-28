"""Local showcase orchestration mirrors the publication build pipeline."""

from __future__ import annotations

from unittest.mock import Mock

from scripts import build_showcase


def test_build_showcase_runs_publication_stages_in_order(monkeypatch) -> None:
    mock_run = Mock()
    monkeypatch.setattr(build_showcase.subprocess, "run", mock_run)

    build_showcase.build_showcase()

    commands = [invocation.args[0] for invocation in mock_run.call_args_list]
    assert [command[-1] for command in commands] == [
        "--metadata-only",
        "scripts/build_showcase_targets.py",
        "--strict",
        "scripts/build_showcase_site.py",
        "scripts/validate_web_output.py",
    ]
    assert all(invocation.kwargs["check"] is True for invocation in mock_run.call_args_list)
    assert all(
        invocation.kwargs["cwd"] == build_showcase.REPOSITORY_ROOT
        for invocation in mock_run.call_args_list
    )

from __future__ import annotations

from dataclasses import dataclass

from tatuy_mcp.access.paths import ProjectPathResolver
from tatuy_mcp.access.policy import DEFAULT_ACCESS_POLICY, AccessPolicy
from tatuy_mcp.config import MCPConfig
from tatuy_mcp.execution.analysis import PythonAnalyzer
from tatuy_mcp.execution.formatting import PythonFormatter
from tatuy_mcp.execution.git import GitWorkspace
from tatuy_mcp.execution.runner import CommandRunner
from tatuy_mcp.execution.testing import TestRunner
from tatuy_mcp.projects.registry import ProjectRegistry
from tatuy_mcp.scaffolding import TatuyScaffolding
from tatuy_mcp.workspace.files import WorkspaceFiles
from tatuy_mcp.workspace.search import WorkspaceSearch


@dataclass(slots=True)
class MCPContext:
    config: MCPConfig
    projects: ProjectRegistry
    paths: ProjectPathResolver
    files: WorkspaceFiles
    search: WorkspaceSearch
    commands: CommandRunner
    formatter: PythonFormatter
    tests: TestRunner
    analysis: PythonAnalyzer
    git: GitWorkspace
    scaffolding: TatuyScaffolding


def create_context(
    config: MCPConfig,
    *,
    policy: AccessPolicy = DEFAULT_ACCESS_POLICY,
) -> MCPContext:
    projects = ProjectRegistry(
        engine_root=config.engine_root,
        projects_root=config.projects_root,
    )
    paths = ProjectPathResolver(projects, policy)
    commands = CommandRunner(
        timeout_seconds=config.command_timeout_seconds,
        max_output=config.max_command_output,
    )
    files = WorkspaceFiles(
        paths,
        policy,
        max_file_bytes=config.max_file_bytes,
        max_read_output=config.max_read_output,
    )
    search = WorkspaceSearch(
        paths,
        policy,
        max_file_bytes=config.max_file_bytes,
    )
    formatter = PythonFormatter(
        projects,
        paths,
        commands,
        max_paths=config.max_command_paths,
    )
    tests = TestRunner(
        projects,
        paths,
        commands,
        max_paths=config.max_command_paths,
    )
    analysis = PythonAnalyzer(
        projects,
        paths,
        commands,
        max_paths=config.max_command_paths,
    )
    git = GitWorkspace(
        projects,
        paths,
        commands,
        max_paths=config.max_command_paths,
    )
    scaffolding = TatuyScaffolding(config, projects)
    return MCPContext(
        config=config,
        projects=projects,
        paths=paths,
        files=files,
        search=search,
        commands=commands,
        formatter=formatter,
        tests=tests,
        analysis=analysis,
        git=git,
        scaffolding=scaffolding,
    )

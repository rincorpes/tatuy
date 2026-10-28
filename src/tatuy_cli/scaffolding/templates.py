from __future__ import annotations

import json
from textwrap import dedent


def _quote(value: str) -> str:
    """Render a string that is valid in TOML."""
    return json.dumps(value, ensure_ascii=False)


def render_app() -> str:
    return dedent(
        """\
        from __future__ import annotations

        from tatuy import TatuyApp, TatuyConfigDict
        from tatuy.ecs.world import World
        from tatuy.scenes.context import Intent, SceneTickContext
        from tatuy.scenes.registry import SceneRegistry
        from tatuy.scenes.scene import Scene


        class MainWorld(World):
            pass


        class MainIntent(Intent):
            pass


        class MainContext(SceneTickContext[MainWorld, MainIntent]):
            pass


        @SceneRegistry.implementation("main")
        class MainScene(Scene[MainWorld, MainIntent, MainContext]):
            world_type = MainWorld
            intent_type = MainIntent
            tick_context_type = MainContext


        def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
            '''Create the reusable Tatuy application.'''
            return TatuyApp(config)


        def main() -> None:
            create_app().run()


        if __name__ == "__main__":
            main()
        """
    )


def render_readme(
    *,
    title: str,
    description: str,
    run_command: str,
    standalone: bool,
) -> str:
    description = description.strip() or "TODO: describe this project."

    if standalone:
        running = (
            "Install dependencies:\n\n"
            "```bash\n"
            "poetry install\n"
            "```\n\n"
            "Run the game:\n\n"
            "```bash\n"
            f"{run_command}\n"
            "```"
        )
    else:
        running = (
            "From the Tatuy repository root:\n\n"
            "```bash\n"
            f"{run_command}\n"
            "```"
        )

    return (
        f"# {title}\n\n"
        f"{description}\n\n"
        "## Goal\n\n"
        "TODO\n\n"
        "## Notes\n\n"
        "TODO\n\n"
        "## Running\n\n"
        f"{running}\n"
    )


def render_manifest(
    *,
    name: str,
    title: str,
    kind: str,
    description: str,
    status: str,
    created_at: str,
    tags: tuple[str, ...],
    tatuy_source: str,
    tatuy_path: str | None = None,
    tatuy_version: str | None = None,
) -> str:
    rendered_tags = ", ".join(_quote(tag) for tag in tags)

    lines = [
        "schema_version = 1",
        "",
        f"name = {_quote(name)}",
        f"title = {_quote(title)}",
        f"kind = {_quote(kind)}",
        f"description = {_quote(description.strip())}",
        f"status = {_quote(status)}",
        f"created_at = {_quote(created_at)}",
        "",
        'entrypoint = "app.py"',
        f"tags = [{rendered_tags}]",
        "",
        "[tatuy]",
        f"source = {_quote(tatuy_source)}",
    ]

    if tatuy_path is not None:
        lines.append(f"path = {_quote(tatuy_path)}")

    if tatuy_version is not None:
        lines.append(f"version = {_quote(tatuy_version)}")

    return "\n".join(lines) + "\n"


def render_web_profile(
    *,
    target_id: str,
    slug: str,
    title: str,
    description: str,
    category: str,
    tags: tuple[str, ...],
    source: str,
    docs: str,
) -> str:
    """Render opt-in showcase metadata without promoting browser support."""
    rendered_tags = "\n".join(f"    - {_quote(tag)}" for tag in tags)
    if not rendered_tags:
        rendered_tags = f"    - {_quote(category)}"
    return (
        "showcase:\n"
        f"  id: {_quote(target_id)}\n"
        f"  slug: {_quote(slug)}\n"
        f"  title: {_quote(title)}\n"
        f"  description: {_quote(description.strip() or title)}\n"
        f"  category: {_quote(category)}\n"
        "  tags:\n"
        f"{rendered_tags}\n"
        f"  source: {_quote(source)}\n"
        f"  docs: {_quote(docs)}\n"
        "  web: false\n"
        "app:\n"
        "  loop: asyncio\n"
    )


def render_pyproject(
    *,
    name: str,
    description: str,
    tatuy_source: str,
    tatuy_path: str | None,
    tatuy_version: str | None,
) -> str:
    package_name = name.replace("_", "-")

    if tatuy_source == "local":
        if tatuy_path is None:
            raise ValueError("Local Tatuy source requires a path")

        dependency = (
            f"tatuy = {{ path = {_quote(tatuy_path)}, develop = true }}"
        )

    elif tatuy_source == "pypi":
        if tatuy_version is None:
            raise ValueError("PyPI Tatuy source requires a version")

        dependency = f'tatuy = "^{tatuy_version}"'

    else:
        raise ValueError(
            f"Unsupported standalone Tatuy source: {tatuy_source}"
        )

    return dedent(
        f"""\
        [tool.poetry]
        name = {_quote(package_name)}
        version = "0.1.0"
        description = {_quote(description.strip())}
        package-mode = false

        [tool.poetry.dependencies]
        python = ">=3.10,<3.13"
        {dependency}
        """
    )


def render_gitignore() -> str:
    return dedent(
        """\
        .env
        .venv/
        venv/

        __pycache__/
        *.py[cod]

        .pytest_cache/
        .mypy_cache/

        build/
        dist/

        .tatuy/
        """
    )

# Installation

Tatuy currently supports Python 3.10 through 3.12.

## Install Tatuy

The minimal runtime/authoring install is:

```bash
pip install tatuy
```

The core does not require Pygame, Pillow, MCP, or repository tooling.

Tatuy currently defaults to the Pygame backend for desktop execution, so a normal desktop game install should use:

```bash
pip install "tatuy[pygame]"
```

Add image capture when needed:

```bash
pip install "tatuy[pygame,capture]"
```

See [Runtime Dependencies and Extras](../internals/runtime-dependencies.md) for the complete extras model.

## Repository development

The repository uses Poetry. Install the full contributor environment from the repository root:

```bash
poetry install -E dev
```

This includes the Pygame backend, capture dependencies, CLI/MCP tooling, and verification tools.

## Run an example

```bash
poetry run python manage.py run example scenes.on_present
```

Nested examples use dot notation:

```bash
poetry run python manage.py run example backend.renderer.shapes
```

Numeric directory prefixes are organizational and are not part of the logical example name.

## External requirements

Interactive Pygame examples require a desktop environment.

MP4 encoding requires FFmpeg, which is not installed by Python packaging.

## Verify the installation

For a desktop installation, if a fundamental example opens a Tatuy window and exits normally, the basic backend environment is working.

For a minimal core installation, this should succeed without Pygame or tooling dependencies installed:

```bash
python -c "import tatuy; from tatuy.ecs import World; from tatuy.scenes import Scene"
```

---

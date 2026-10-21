# Installation

Tatuy currently supports Python 3.10 through 3.12.

The repository uses Poetry.

## Install dependencies

From the repository root:

```bash
poetry install
```

## Run an example

```bash
poetry run python manage.py run example scenes.on_present
```

Nested examples use dot notation:

```bash
poetry run python manage.py run example backend.renderer.shapes
```

Numeric directory prefixes are organizational and are not part of the logical example name.

## Optional dependencies

Interactive examples require a desktop environment.

MP4 encoding requires FFmpeg.

## Verify the installation

If a fundamental example opens a Tatuy window and exits normally, the basic environment is working.

---

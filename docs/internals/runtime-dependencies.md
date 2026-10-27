# Runtime Dependencies and Extras

Tatuy separates the Python authoring/runtime core from platform backends and development tooling. The source distribution may contain backend and tooling packages, but importing the core must not require their third-party dependencies.

## Core install

The minimal install is:

```bash
pip install tatuy
```

The core dependency set currently contains only `onomasticon`, which is used by Tatuy's implementation registries.

A core install is expected to support importing the public authoring API, ECS, scenes, features, semantic rendering data, engine/runtime contracts, and capture/replay types that do not actually encode images.

It does **not** imply that the default desktop backend can run. `TatuyApp` currently defaults to the Pygame backend, so desktop execution requires the Pygame extra.

## Extras

### `pygame`

```bash
pip install "tatuy[pygame]"
```

Installs the reference Pygame backend using the `pygame-ce` distribution. Tatuy still imports the standard `pygame` module API; `pygame-ce` is the canonical distribution because it is shared by the verified desktop/browser toolchain. Pygame remains a backend implementation dependency, not a requirement of ECS, scenes, semantic rendering, or future SDL/native hosts.

### `capture`

```bash
pip install "tatuy[capture]"
```

Installs Pillow for screenshot/frame image encoding. Capture modules remain importable without Pillow; Pillow is loaded only when image encoding is requested.

FFmpeg is an external executable requirement for MP4 encoding and is not installed by Python packaging.

Installing the `capture` extra and enabling the capture runtime capability are separate decisions. Desktop behavior remains unchanged by default: capture is enabled. A host that cannot or should not provide capture can disable it without changing game code:

```python
TatuyApp({
    "capabilities": {
        "capture": False,
    }
})
```

When disabled, Tatuy composes `NullCaptureService` instead of `CaptureService`. The concrete capture/worker/video stack is imported lazily only when capture is enabled, no capture worker is started, media-capture hotkeys are not reserved, and engine/render lifecycle code continues through the same `CaptureCapability` contract. Replay is a separate capability and can remain enabled or disabled independently.

`RuntimeServices.defaults(backend, capture_enabled=False)` exposes the same lower-level composition switch for hosts that construct the engine without `TatuyApp`.

### `web`

```bash
pip install "tatuy[web]"
```

Installs the browser packaging/build stack without pulling in capture, CLI, or MCP tooling. The current web extra includes `pygame-ce`, Pygbag, and PyYAML. Pygbag remains build-time tooling: exported games do not need to import it at runtime, and gameplay modules remain unaware of the browser packager.

For repository development, the W6 builder can use the active environment directly once this extra is installed; `--pygbag-python` remains available for explicit interpreter selection.

### `cli`

```bash
pip install "tatuy[cli]"
```

Installs the Limen dependency used by `tatuy_cli`. The CLI is repository/developer tooling and is not required by a game runtime.

### `mcp`

```bash
pip install "tatuy[mcp]"
```

Installs the MCP SDK and dotenv support used by `tatuy_mcp`. The engine runtime must never import MCP infrastructure merely to import or execute normal Tatuy code.

### `tooling`

```bash
pip install "tatuy[tooling]"
```

Installs the optional capture, CLI, and MCP third-party dependencies together. It intentionally does not install the Pygame backend or browser packaging stack because platform/backend selection and web-build tooling remain separate concerns.

### `dev`

```bash
pip install "tatuy[dev]"
```

Installs the full contributor environment: the `pygame-ce` reference backend, browser packaging (`pygbag` + PyYAML), capture, CLI/MCP dependencies, tests, formatting, type checking, and linting.

For the repository's Poetry workflow, use:

```bash
poetry install -E dev
```

## Dependency classification

| Dependency | Classification | Reason |
| --- | --- | --- |
| `onomasticon` | core | implementation registries used by engine-facing code |
| `pygame-ce` | `pygame` / `web` / `dev` | canonical Pygame distribution for desktop and verified browser packaging |
| `pygbag` | `web` / `dev` | browser packaging tool used by the W6 adapter |
| `pyyaml` | `config` / `web` / `dev` | layered YAML configuration and web profile loading |
| `pillow` | `capture` / `tooling` | screenshot and frame image encoding |
| `rincorpes-limen` | `cli` / `tooling` | `tatuy_cli` command framework |
| `mcp[cli]` | `mcp` / `tooling` | Tatuy Development MCP server |
| `python-dotenv` | `mcp` / `tooling` | MCP configuration loading |
| `relict` | removed | no current source usage |

## Import boundary

The packaging contract is stronger than merely declaring extras in `pyproject.toml`:

```text
import tatuy
import tatuy.ecs
import tatuy.scenes
import tatuy.features.*
```

must not import Pygame, Pillow, MCP, Limen, or dotenv as a side effect.

Optional dependencies should therefore be imported at the implementation boundary that needs them. For example, `tatuy.capture.worker` loads Pillow only when an image job is processed.

Backend discovery follows the same rule: selecting `pygame` may import Pygame, but importing backend-neutral contracts must not.

## Future native/browser packaging

The current extras establish the intended direction without committing to the final native package name:

```text
tatuy
    Python authoring/runtime core

tatuy[pygame]
    reference Pygame backend via pygame-ce

tatuy[web]
    browser packaging/build requirements

tatuy[tooling]
    optional development/capture tooling

future tatuy[native]
    native bindings/runtime when implemented
```

A future SDL/native/browser host must be able to depend on the core without inheriting Pygame, MCP, Pillow, or desktop tooling automatically.

---
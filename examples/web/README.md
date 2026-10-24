# Web Spikes

These targets exercise Tatuy's browser-hosting path without changing the canonical desktop fundamentals.

The first spike uses the current local Tatuy source, `pygame-ce`, and Pygbag. Browser-specific behavior remains opt-in: normal `TatuyApp.run()` and the upstream-Pygame Poetry environment are unchanged.

## 001 Render Queue

The tracked source lives in:

```text
examples/web/001_render_queue/main.py
```

Pygbag packages one project directory, so prepare an ignored staging directory containing the spike, the current local `src/tatuy` package, and Tatuy's required pure-Python runtime dependencies such as `onomasticon`:

```powershell
poetry run python scripts/prepare_web_spike.py
```

The preparation command prints the exact content-addressed staging directory, for example `001_render_queue-a1b2c3d4`. Run Pygbag against that printed path. Force the browser runtime to Python 3.12, skip the media-engagement gate for this no-audio spike, and use the dedicated local port:

```powershell
.\.venv-web\Scripts\python.exe -m pygbag --PYBUILD 3.12 --ume_block 0 --port 8766 .tatuy\web-spike\001_render_queue-<fingerprint>
```

The preparation command also prints cache-safe browser URLs. Use those exact URLs instead of a reused root URL. They request `/index.html` explicitly and include `TATUY_BUILD=<fingerprint>` so the top-level HTML/bootstrap document changes identity together with the application archive:

```text
http://localhost:8766/index.html?PYGPI=http://localhost:8766/cdn/&TATUY_BUILD=<fingerprint>#
```

Use the printed interactive URL when needed; it adds `&-i#` after the build identifier.

Keep the `PYGPI` value literal. Pygbag 0.9.3 treats query `KEY=VALUE` environment variables as raw strings rather than URL-decoding percent escapes, so percent-encoding `http://...` produces a malformed package-index URL.

The target keeps an explicit top-level `import pygame` because Pygbag discovers WASM package dependencies from `main.py`; Tatuy itself loads the concrete Pygame backend dynamically. It also disables capture and uses `TatuyApp.run_async()`. None of these browser-spike requirements change the normal desktop runtime path.

Re-running `prepare_web_spike.py` removes prior spike staging directories and creates a content-addressed directory whose name changes whenever packaged source or bundled dependency content changes. Pygbag therefore serves a new archive URL instead of relying on browser cache invalidation.

For browser input verification, hold `W` to move the blue rectangle upward and move the pointer inside the canvas to make the orange circle follow it. The default positions remain the original render-queue proof when no input is active.

## Compatibility gate

Before treating `pygame-ce` as supported, run Tatuy's Pygame backend tests inside `.venv-web` so they execute against the `pygame` namespace provided by `pygame-ce` rather than upstream `pygame`.

```powershell
.\.venv-web\Scripts\python.exe -m pip install pytest
.\.venv-web\Scripts\python.exe -m pytest tests/src/tatuy/backend/pygame
```

Do not add `pygame-ce` or Pygbag to Tatuy's normal Poetry dependency model until the spike and backend compatibility tests justify that decision.

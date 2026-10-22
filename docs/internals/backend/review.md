# Backend review — 2026-10-22

## Scope and outcome

Reviewed the shared backend contracts/configuration/factory/registry, all
Pygame capability implementations, backend documentation, existing tests,
fundamental backend examples, and relevant application/engine/window/audio
callers.

The existing capability split is suitable for the current engine. Keep the
factory/builder/registry arrangement and narrow capability interfaces.
The immediate work is correctness and explicit contracts; the evidence does
not justify a new abstraction layer or moving the backend to C++.

No production implementation files were changed in this review.

## Work applied

- Added 11 Python test files under `tests/src/tatuy/backend/`, mirroring
  `src/tatuy/backend/`, including `pygame/components/`.
- Added 64 backend test cases: 57 pass and 7 are strict expected failures.
- Repaired the existing `tests/conftest.py` report hook by adding its
  required `yield`. Before that change pytest failed during setup because
  a hook wrapper was not a generator.
- Replaced 16 incomplete/placeholder documentation pages with current APIs,
  configuration examples, lifecycle sequencing, capability behavior,
  errors, limitations, and verification guidance.

Expected-failure tests are executable proposals for the intended behavior
described below. They do not silently endorse existing defects.
With `strict=True`, a future unexpected pass fails the suite so the marker
must be removed when a fix is accepted.

## Findings requiring implementation decisions

### B01 — Resolved: startup failures can leak platform resources

Implemented after this review: backend initialization now rolls back on
failure, repeated initialization preserves capabilities, and failed platform
cleanup can be retried. PythonLoop includes startup in its cleanup boundary
and preserves the original error when cleanup also fails. The original B01
regression is now a passing test; lifecycle and loop regressions cover the
additional failure paths. See [Lifecycle](lifecycle.md) for the contract.

Original finding:

Locations: `pygame/pygame_backend.py:PygameBackend.init/stop` and
`engine/loop/python_loop.py:PythonLoop.run`.

After `pygame.init()`, a capability constructor or audio setup can raise.
The backend flag remains false, and `stop()` therefore does not call
`pygame.quit()`. The loop also calls `engine.start()` before entering its
cleanup block, so a window/scene startup exception bypasses normal cleanup.

Reproduced by making renderer construction fail and then calling stop:
Pygame quit is never called.

Recommended approach: make backend initialization transactional with cleanup
on failure, then move engine startup into an appropriate cleanup boundary.
Define how repeated init and cleanup failures behave. Retain the SDL window
wrapper lifetime protection. This changes exceptional-path runtime behavior
and needs agreement before implementation.

Regression: `pygame/test_pygame_backend.py::test_failed_initialization_releases_platform`.

### B02 — Medium: disabled audio is not consistently a no-op

Location: `pygame/components/audio.py:PygameAudio.set_master_volume/stop_all`.

Disabled init/load/play/shutdown return early, but master volume and stop-all
still call the mixer. Calling the public service with disabled or unavailable
audio can therefore reach an uninitialized mixer.

Recommended approach: consistently guard device operations when disabled,
and define behavior when enabled but not initialized. Separately decide
whether parent `pygame.init()` should initialize the mixer at all when
audio is disabled or auto-init is false; its current global initialization
does not enforce those flags as device-lifetime guarantees.

Regression: `pygame/components/test_audio.py::test_disabled_volume_and_stop_are_noops`.

### B03 — Medium: sounds loaded later ignore master volume

Location: `pygame/components/audio.py:PygameAudio.load_sound/set_master_volume`.

Setting master volume changes music and currently loaded sounds only. A sound
loaded afterward receives no volume adjustment. For example, set master to
32/128 and load a new effect: the new effect does not inherit 0.25 gain.

Recommended minimal fix: retain the selected master volume and apply it
during loading. Decide whether per-sound volume overrides master or whether
effective volume should be master multiplied by per-sound gain. Multiplicative
gains are a broader behavior change and should be treated separately.

Regression: `pygame/components/test_audio.py::test_later_sound_inherits_master_volume`.

### B04 — Medium: concrete capture does not satisfy its path contract

Locations: `protocols/capture.py:Capture.bmp`,
`pygame/components/capture.py:PygameCapture.bmp`, and `pygame/builder.py`.

The protocol accepts an omitted or None path; Pygame requires a positional
string. A valid protocol call `capture.bmp()` raises TypeError.
The builder's cast prevents ordinary mypy checking from proving structural
compatibility.

Recommended approach: accept the protocol's optional/default argument and
return false when no path is provided, matching the existing empty-path
behavior. Alternative: make explicit paths required in all contracts and
callers; that changes the public protocol.

After aligning the contract, reassess whether the cast can be replaced by
actual structural checking. Do not remove it mechanically without inspecting
any additional protocol diagnostics.

Regression: `pygame/components/test_capture.py::test_capture_accepts_protocol_default_path`.

### B05 — Medium: translucent polygons lose their maximum-edge pixels

Location: `pygame/components/renderer.py:PygameShape.polygon`.

The temporary rectangle uses `max_x - min_x` and `max_y - min_y`.
Pygame rasterization includes vertex pixels, but those temporary dimensions
exclude the maximum coordinate. A translucent square from (2,2) to (8,8)
leaves pixel (8,5) untouched.

Recommended approach: include the maximum raster boundary in temporary
surface bounds, preserving screen/active-clip handling. Compare opaque and
alpha coverage at all edges and at viewport scales.

Regression: `pygame/components/test_renderer.py::test_alpha_polygon_includes_last_vertex`.

### B06 — Medium: tiled textures bypass viewport transformation

Location: `pygame/components/renderer.py:PygameTexture.tiled`.

Normal texture drawing maps position and dimensions. Tiled drawing uses raw
coordinates and width, so it appears at the wrong location/scale when the
viewport is offset or scaled. Missing handles also raise KeyError here but
are silently ignored by ordinary draw.

Recommended approach: make tiling obey logical coordinates like other
renderer methods, including a clearly defined scaled tile height and final
crop. Decide whether the current operation remains vertical-only or becomes
two-axis tiling; do not expand its scope implicitly.

Regression: `pygame/components/test_renderer.py::test_tiled_texture_uses_viewport`.

### B07 — Medium: a literal default alias overrides the configured font

Location: `pygame/components/renderer.py:PygameText._resolve_font_path`.

When fonts contain both "default" and "ui" and `default_font="ui"`, drawing
without an explicit name uses "default". The requested default is ignored
because lookup prioritizes the literal alias.

Recommended approach: omitted names use the configured default; specify an
independent fallback policy for unknown explicit names. This changes output
for existing configurations that rely on the current precedence.

Regression: `pygame/components/test_renderer.py::test_configured_default_font_is_selected`.

## Other contract and maintenance decisions

These observations are from source inspection; they are not additional
native-platform defects established by the seven regression cases.

| Area | Observation | Proposed next step |
| --- | --- | --- |
| Input configuration | Keyboard/mouse/gamepad flags are unused; modifier/keypad/gamepad coverage is incomplete | Decide supported input scope, then implement or deprecate misleading fields |
| Capture configuration | Port ignores enabled/directory/format; higher-level settings also exist | Define ownership before removing or enforcing fields |
| Text sizes | FontConfig.size is unused; omitted size does not scale like explicit size | Choose a default-size rule and add focused tests |
| Shape sizing | Line thickness stays in screen pixels; zero/negative circles become at least one pixel | Agree logical-versus-screen units and invalid-input policy |
| Texture validation | Positive pitch smaller than width*4 and invalid dimensions are not explicitly rejected | Validate dimensions/row pitch before allocation/conversion |
| Native window resize | WindowService invokes set_mode on native resize notifications | Reproduce on desktop before changing event-driven resize policy |
| Boundary portability | Window.screen is Any; window event dictionaries may contain native values | Audit concrete consumers before implementing another backend |
| Error types | Pygame config declares a separate unused BackendConfigError; PygameBackendError is not a BackendError subclass | Agree a consistent exception hierarchy; avoid silently changing public catches |
| Renderer output | set_clear_color prints to stdout | Remove the debug print in an approved cleanup |
| Examples | Several examples initialize outside their cleanup block; window example ignores QUIT | Update cleanup/exit patterns alongside an accepted lifecycle fix |
| Test markers | Sample unit/integration markers are unregistered | Register intended markers or remove sample markers in test maintenance |

## Static analysis

Executed mypy for `src/tatuy/backend` alone: no issues in 26 source files.
Executed mypy for backend plus new tests: no issues in 37 source files.
These results do not establish full backend substitutability because the
builder uses a cast and many functions have unannotated bodies.

Pylint exits 28: warning, refactor, and convention categories, with no
reported fatal/error category. Findings include:

- W0611: unused imports left in shared config after decoding moved to
  `dataclass_utils`. These are mechanical cleanup candidates.
- C0114/C0115/C0116: missing module/class/function docstrings. Existing
  external docs also disagreed with implemented behavior in places; this
  review updated the Markdown docs, not production docstrings.
- R0914/R0911: renderer locals and event-translation returns exceed configured
  thresholds. Extract helpers only if it improves clarity without degrading
  hot paths; do not restructure solely to satisfy counts.
- R0913/R0917/R0902: protocol argument counts and composed backend attribute
  counts. These mostly reflect the chosen API/composition. Changing public
  signatures or weakening configuration is not justified by these warnings
  alone.

No new casts, ignores, pylint disables, or checker configuration changes
were introduced. Pylint's configuration excludes tests from normal analysis;
including their directory in the command is not proof they were linted.

## Verification actually executed

| Check | Result |
| --- | --- |
| Initial full pytest | Blocked by pre-existing invalid hook wrapper |
| Backend pytest after test-hook repair | 57 passed, 7 expected failures |
| Full repository pytest | 60 passed, 7 expected failures, 2 existing unknown-marker warnings |
| Selected regression tests with --runxfail | All 7 fail for the documented assertions/signature mismatch |
| Backend mypy | Clean, 26 files |
| Backend and new-test mypy | Clean, 37 files |
| Backend pylint, also requesting test directory | Existing findings, exit 28; tests excluded by configuration |
| Formatting | New test contents verified against configured isort and Black output |

The explicit regression run also emitted sandbox cache-write warnings;
the plugin-driven normal suite completed without those cache warnings.

Not executed: interactive examples, native display/SDL wrapper lifetime
stress tests, actual audio playback/device-failure tests, real font-file
loading, driver-specific rendering, FFmpeg/video encoding, cross-platform
runs, performance benchmarks, or coverage measurement.

Unit tests use offscreen surfaces and mocks. Texture tests validate row
repacking and pixels with display conversion substituted, so actual
convert_alpha/display behavior still needs an integration smoke test.

## Suggested implementation order

1. Resolve B01 lifecycle cleanup, including runtime startup.
2. Fix B05 polygon bounds and B06 viewport-consistent tiling.
3. Decide and apply B02/B03 audio-state and gain behavior.
4. Align B04 capture signature and B07 font selection.
5. Decide the remaining config/validation policies.
6. Measure rendering workloads before optimizing.

Per-shape alpha-surface allocation, repeated texture scaling/rotation, and
unbounded font cache growth are plausible performance pressure points.
They are candidates for measurement, not measured bottlenecks from this
review.

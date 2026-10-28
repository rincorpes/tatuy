# Web Compatibility Matrix

This matrix tracks every runnable fundamental under `examples/fundamentals` and records whether it is a candidate for the Tatuy browser showcase.

The current showcase scope is **fundamentals only**. Experiments and games are intentionally deferred until they are explicitly promoted into the public showcase.

## Status legend

| Status | Meaning |
| --- | --- |
| `Playable` | Declared, packaged, manually browser-verified, and eligible for the public showcase. |
| `Candidate` | Uses the reusable Tatuy application/runtime path and has no known browser-specific blocker. It still needs a browser smoke test before public promotion. |
| `W12 input` | Expected to work structurally; representative browser input/focus behavior is now verified, but this specific target has not been promoted yet. |
| `W13 audio` | Requires the browser-audio/user-gesture work planned for W13. |
| `W13 asset` | Browser audio behavior is verified, but the target still needs a browser-safe audio asset before public promotion. |
| `W13 verify` | Has gesture-gated audio, packaged assets, and mute/error handling; requires a real browser sound smoke test before `web: true` promotion. |
| `Host/API only` | Demonstrates backend, engine, loop, or host construction directly rather than a normal game target. Keep as documentation/source unless deliberately adapted. |
| `Unsupported v0` | Demonstrates a capability intentionally disabled in browser-v0. |

## Fundamentals

| Target | Category | Web status | Blocker / next gate | Assets | Input | Audio | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `001_backend` | backend | Host/API only | Direct `PygameBackend` construction | none | backend events | no | Backend overview, not a normal hosted game target. |
| `001_backend/001_basic_config` | backend | Host/API only | Direct backend configuration | none | none | no | Configuration API demonstration. |
| `001_backend/002_dict_config` | backend | Host/API only | Direct backend configuration | none | none | no | Dictionary configuration demonstration. |
| `001_backend/003_factory` | backend | Host/API only | Direct backend factory | none | none | no | Backend discovery/construction demonstration. |
| `001_backend/004_window` | backend | Host/API only | Direct window/backend lifecycle | none | none | no | Host/window API demonstration. |
| `001_backend/005_events` | backend | Host/API only | Direct backend event polling | none | backend events | no | Browser event behavior belongs behind the hosted runtime. |
| `001_backend/006_input` | backend | Host/API only | Direct backend input polling | none | keyboard/mouse | no | Use W12 to verify game-facing input instead. |
| `001_backend/007_renderer` | backend | Host/API only | Direct renderer/backend lifecycle | none | none | no | Renderer API demonstration. |
| `001_backend/007_renderer/001_shapes` | backend renderer | Host/API only | Direct renderer/backend lifecycle | none | none | no | Rendering primitive demonstration. |
| `001_backend/007_renderer/002_text` | backend renderer | Host/API only | Direct renderer/backend lifecycle | none | none | no | Text rendering primitive demonstration. |
| `001_backend/007_renderer/003_textures` | backend renderer | Host/API only | Direct renderer/backend lifecycle | none | none | no | Texture API demonstration. |
| `001_backend/007_renderer/004_clipping` | backend renderer | Host/API only | Direct renderer/backend lifecycle | none | none | no | Clipping API demonstration. |
| `001_backend/007_renderer/005_viewport` | backend renderer | Host/API only | Direct renderer/backend lifecycle | none | none | no | Viewport API demonstration. |
| `001_backend/008_audio` | backend audio | W13 audio | Browser audio unlock + direct backend path | `assets/test.wav` | terminal `input()` | yes | Also uses terminal input and a host-relative asset path. |
| `001_backend/008_audio/001_autoload` | backend audio | W13 audio | Browser audio unlock + direct backend path | local audio asset | none | yes | Backend-level audio demonstration. |
| `001_backend/009_capture` | backend capture | Unsupported v0 | Capture disabled in browser-v0 | none | none | no | Keep desktop-only until browser capture is deliberately designed. |
| `001_backend/009_capture/001_raw` | backend capture | Unsupported v0 | Capture disabled in browser-v0 | none | none | no | Raw capture demonstration. |
| `002_running/001_engine` | runtime | Host/API only | Direct engine construction | none | none | no | Demonstrates engine ownership below `TatuyApp`. |
| `002_running/002_loop` | runtime | Host/API only | Explicit loop ownership | none | none | no | Loop behavior is host-owned in browser builds. |
| `002_running/003_runtime` | runtime | Host/API only | Explicit runtime/host composition | none | none | no | Useful architecture example, not a showcase game target. |
| `002_running/004_app` | runtime | Candidate | Browser smoke test | none | none | no | Uses the reusable `TatuyApp` seam. |
| `003_scenes` | scenes | Host/API only | Legacy direct `PygameBackend + Engine + PythonLoop` composition | none | none | no | Should remain an architecture example or be migrated before promotion. |
| `003_scenes/001_world` | scenes | Candidate | Browser smoke test | none | no meaningful input | no | Uses `TatuyApp`; `InputFrame` is accepted but not consumed. |
| `003_scenes/002_intent` | scenes | Candidate | Browser smoke test | none | no meaningful input | no | Demonstrates intent construction without depending on a specific input value. |
| `003_scenes/003_context` | scenes | W12 input | Mouse-inside/focus semantics | none | mouse-inside | no | Requires browser canvas focus/pointer validation. |
| `003_scenes/004_on_tick` | scenes | Candidate | Browser smoke test | none | no meaningful input | no | No known browser-specific dependency. |
| `003_scenes/005_build_intent` | scenes | W12 input | Mouse-inside/focus semantics | none | mouse-inside | no | Requires browser canvas focus/pointer validation. |
| `003_scenes/006_on_present` | scenes | Playable | None for current v0 | none | mouse-inside + focus | no | Browser-verified pointer-inside and focus-state visualization. |
| `004_ecs/001_resources` | ECS | W12 input | Mouse-inside/focus semantics | none | mouse-inside | no | Uses pointer state to mutate a resource. |
| `004_ecs/002_entities` | ECS | W12 input | Mouse-inside/focus semantics | none | mouse-inside | no | Uses pointer state to drive entity count. |
| `004_ecs/002_entities/001_factory` | ECS | W12 input | Mouse-inside/focus semantics | none | mouse-inside | no | Factory variant of the entity example. |
| `004_ecs/003_components` | ECS | W12 input | Mouse-inside/focus semantics | none | mouse-inside | no | Uses pointer state while demonstrating components. |
| `004_ecs/003_components/001_query` | ECS | W12 input | Mouse-inside/focus semantics | none | mouse-inside | no | Query variant of the components example. |
| `004_ecs/004_systems` | ECS | W12 input | Mouse-inside/focus semantics | none | mouse-inside | no | Uses pointer state while demonstrating systems. |
| `005_multiple_scenes` | scenes | Playable | None for current v0 | none | Enter + mouse-inside | no | Browser-verified discrete Enter presses and scene transitions. |
| `006_shared_scene_settings` | scenes | W12 input | Enter key + mouse-inside/focus | none | Enter + mouse-inside | no | Shared settings are host-safe; controls need W12. |
| `007_transform_component` | spatial | Candidate | Browser smoke test | none | no meaningful input | no | No known browser-specific dependency. |
| `008_visual_components/001_rect` | visual | Candidate | Browser smoke test | none | no meaningful input | no | Pure visual component example. |
| `008_visual_components/002_circle` | visual | Candidate | Browser smoke test | none | no meaningful input | no | Pure visual component example. |
| `008_visual_components/003_polygon` | visual | Candidate | Browser smoke test | none | no meaningful input | no | Pure visual component example. |
| `008_visual_components/004_text` | visual | Candidate | Browser smoke test | none | no meaningful input | no | Text uses backend font support but no local font asset. |
| `009_rendering/001_render_system` | rendering | Candidate | Browser smoke test | none | no meaningful input | no | Hosted rendering path candidate. |
| `009_rendering/002_render_queue` | rendering | Playable | None for current v0 | none | no meaningful input | no | First canonical browser-playable target. |
| `009_rendering/003_canvas` | rendering | Candidate | Browser smoke test | none | no meaningful input | no | Canvas API candidate. |
| `009_rendering/004_layers_and_z` | rendering | Candidate | Browser smoke test | none | no meaningful input | no | Layer/z-order candidate. |
| `010_movement/001_velocity_integration` | movement | Candidate | Browser smoke test | none | no meaningful input | no | Autonomous movement. |
| `010_movement/002_movement_system` | movement | Candidate | Browser smoke test | none | no meaningful input | no | Autonomous movement system. |
| `010_movement/003_controlled_movement` | movement | Playable | None for current v0 | none | WASD | no | Browser-verified held WASD input, focus loss recovery, and scroll suppression. |
| `011_collisions/001_detection` | collision | Candidate | Browser smoke test | none | no meaningful input | no | No known browser-specific dependency. |
| `011_collisions/002_response` | collision | Candidate | Browser smoke test | none | no meaningful input | no | No known browser-specific dependency. |
| `011_collisions/003_sensors` | collision | Candidate | Browser smoke test | none | no meaningful input | no | No known browser-specific dependency. |
| `011_collisions/004_custom_response_rule` | collision | Candidate | Browser smoke test | none | no meaningful input | no | No known browser-specific dependency. |
| `012_bounds/001_behavior` | bounds | Candidate | Browser smoke test | none | no meaningful input | no | No known browser-specific dependency. |
| `013_lifecycle/001_lifetime` | lifecycle | Candidate | Browser smoke test | none | no meaningful input | no | No known browser-specific dependency. |
| `013_lifecycle/002_respawn` | lifecycle | Candidate | Browser smoke test | none | no meaningful input | no | No known browser-specific dependency. |
| `013_lifecycle/003_runtime_spawn_queue` | lifecycle | Candidate | Browser smoke test | none | no meaningful input | no | No known browser-specific dependency. |
| `014_particles` | FX | Candidate | Browser smoke test | none | no meaningful input | no | Particle processing candidate. |
| `015_trails` | FX | Candidate | Browser smoke test | none | no meaningful input | no | Trail rendering candidate. |
| `016_camera_effects` | FX | Candidate | Browser smoke test | none | no meaningful input | no | Camera-effects candidate. |
| `017_screen_effects` | FX | Candidate | Browser smoke test | none | no meaningful input | no | Screen-effects candidate. |
| `018_audio` | audio | W13 asset | Replace WAV with browser-safe OGG before public promotion | packaged `assets/test.wav` (local smoke only) | SPACE + M | yes | Chromium verified gesture unlock, playback, repeated playback, and mute/unmute; strict Pygbag builds still reject the WAV asset. |
| `020_ui/001_panel_layout` | UI | Candidate | Browser smoke test | none | no meaningful input | no | Layout-only UI example. |
| `020_ui/002_text` | UI | Candidate | Browser smoke test | none | no meaningful input | no | Text-only UI example. |
| `020_ui/003_button` | UI | Playable | None for current v0 | none | pointer/button | no | Browser-verified pointer hover, press, release, and click interaction. |

## Legacy/non-runnable directories

`008_graphic_components` contains empty historical directories and `009_render_system` is empty. They have no runnable `app.py`, are not resolved as CLI targets, and should remain outside the public catalog unless deliberately restored.

## W12 browser input smoke test

W12 browser verification passed on October 28, 2026 for the four representative input targets:

```powershell
poetry run python scripts/build_web_target.py examples/fundamentals/003_scenes/006_on_present
poetry run python scripts/build_web_target.py examples/fundamentals/005_multiple_scenes
poetry run python scripts/build_web_target.py examples/fundamentals/010_movement/003_controlled_movement
poetry run python scripts/build_web_target.py examples/fundamentals/020_ui/003_button
```

The manual pass confirmed pointer/focus state, discrete Enter presses, held WASD movement, UI pointer interaction, focus-loss recovery without stuck input, and browser-scroll suppression while gameplay is focused. Those four targets are now promoted to `showcase.web: true` and `Playable`.

Resize/high-DPI scaling remains W14 scope.

## W13 browser audio smoke test

Chromium verification passed on October 28, 2026 for the game-facing audio fundamental using the developer-only sound-format override:

```powershell
poetry run python scripts/build_web_target.py examples/fundamentals/018_audio --allow-unsupported-sound-format
```

The manual pass confirmed that the game starts before audio unlock, `SPACE` unlocks and plays sound, repeated playback works, and `M` mutes/unmutes while preserving the previous master volume.

Strict Pygbag packaging correctly rejects the current WAV as a common unsupported browser format. The override above exists only for local W13 runtime smoke testing; normal builds remain strict. Before `018_audio` can change to `showcase.web: true`, replace the staged WAV with a browser-safe OGG, update the target to load the OGG logical asset, and repeat the strict build/browser smoke test without the override.

## W15 GitHub Pages base-path safety

The composed showcase is intentionally base-path agnostic: internal shell, docs, assets, and runtime links are relative rather than rooted at `/`. Tests resolve those links beneath `https://rincorpes.github.io/tatuy/` and verify that home, docs, showcase pages, raw playables, and shared assets remain inside the `/tatuy/` project path.

`ShowcaseSiteBuilder` also validates the generated HTML/CSS tree and rejects root-absolute internal references such as `/assets/...` or `/play/...`. External URLs and in-page anchors remain allowed. MkDocs declares the canonical documentation URL as `https://rincorpes.github.io/tatuy/docs/`.

## Promotion rules

A `Candidate` target is not automatically public. Before adding `showcase` metadata with `web: true`, the target should:

1. pass the relevant W12/W13 gate when it consumes input or audio;
2. build successfully through `WebTargetBuilder`;
3. load beneath the GitHub Pages project subpath;
4. have a useful title, description, category, tags, source path, and related docs;
5. avoid capture/replay or other browser-v0-disabled capabilities unless the corresponding browser support exists.

The matrix intentionally does not include experiments or games. The current showcase scope is fundamentals; those categories can be audited later if they are explicitly promoted.

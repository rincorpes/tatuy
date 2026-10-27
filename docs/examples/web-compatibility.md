# Web Compatibility Matrix

This matrix tracks every runnable fundamental under `examples/fundamentals` and records whether it is a candidate for the Tatuy browser showcase.

The current showcase scope is **fundamentals only**. Experiments and games are intentionally deferred until they are explicitly promoted into the public showcase.

## Status legend

| Status | Meaning |
| --- | --- |
| `Playable` | Already declared, packaged, and used by the browser showcase. |
| `Candidate` | Uses the reusable Tatuy application/runtime path and has no known browser-specific blocker. It still needs a browser smoke test before public promotion. |
| `W12 input` | Expected to work structurally, but meaningful keyboard/mouse/focus behavior must be verified during the browser-input phase. |
| `W13 audio` | Requires the browser-audio/user-gesture work planned for W13. |
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
| `003_scenes/006_on_present` | scenes | W12 input | Mouse-inside/focus semantics | none | mouse-inside | no | Visualizes whether the pointer is inside the canvas. |
| `004_ecs/001_resources` | ECS | W12 input | Mouse-inside/focus semantics | none | mouse-inside | no | Uses pointer state to mutate a resource. |
| `004_ecs/002_entities` | ECS | W12 input | Mouse-inside/focus semantics | none | mouse-inside | no | Uses pointer state to drive entity count. |
| `004_ecs/002_entities/001_factory` | ECS | W12 input | Mouse-inside/focus semantics | none | mouse-inside | no | Factory variant of the entity example. |
| `004_ecs/003_components` | ECS | W12 input | Mouse-inside/focus semantics | none | mouse-inside | no | Uses pointer state while demonstrating components. |
| `004_ecs/003_components/001_query` | ECS | W12 input | Mouse-inside/focus semantics | none | mouse-inside | no | Query variant of the components example. |
| `004_ecs/004_systems` | ECS | W12 input | Mouse-inside/focus semantics | none | mouse-inside | no | Uses pointer state while demonstrating systems. |
| `005_multiple_scenes` | scenes | W12 input | Enter key + mouse-inside/focus | none | Enter + mouse-inside | no | Scene transition behavior needs browser keyboard/focus validation. |
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
| `010_movement/003_controlled_movement` | movement | W12 input | WASD + focus/scroll conflicts | none | WASD | no | Primary keyboard-input smoke-test candidate. |
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
| `018_audio` | audio | W13 audio | Browser audio unlock/user gesture | `assets/test.wav` | no meaningful input | yes | Uses the logical `ctx.assets` boundary; structurally ready once audio policy is implemented. |
| `020_ui/001_panel_layout` | UI | Candidate | Browser smoke test | none | no meaningful input | no | Layout-only UI example. |
| `020_ui/002_text` | UI | Candidate | Browser smoke test | none | no meaningful input | no | Text-only UI example. |
| `020_ui/003_button` | UI | W12 input | Pointer/focus/click semantics | none | pointer/button | no | Primary UI pointer-input smoke-test candidate. |

## Legacy/non-runnable directories

`008_graphic_components` contains empty historical directories and `009_render_system` is empty. They have no runnable `app.py`, are not resolved as CLI targets, and should remain outside the public catalog unless deliberately restored.

## Promotion rules

A `Candidate` is not automatically public. Before adding `showcase` metadata with `web: true`, the target should:

1. pass the relevant W12/W13 gate when it consumes input or audio;
2. build successfully through `WebTargetBuilder`;
3. load beneath the GitHub Pages project subpath;
4. have a useful title, description, category, tags, source path, and related docs;
5. avoid capture/replay or other browser-v0-disabled capabilities unless the corresponding browser support exists.

The matrix intentionally does not include experiments or games. The current showcase scope is fundamentals; those categories can be audited later if they are explicitly promoted.

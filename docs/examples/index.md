# Examples

Tatuy examples are executable documentation.

```text
examples/
├── fundamentals/
├── experiments/
└── games/
```

Topic indexes:

- [Experiments](experiments.md)
- [Games](games.md)

## Fundamentals map

Fundamentals teach one concept with minimal unrelated behavior. Use this table to jump from a concept to executable source and the corresponding documentation.

| Concept | Executable example | Learn / guide |
| --- | --- | --- |
| Backend/platform primitives | `examples/fundamentals/001_backend/` | Backend/internals documentation |
| Runtime/loop primitives | `examples/fundamentals/002_running/` | [Runtime](../learn/runtime.md) |
| Scene basics | `examples/fundamentals/003_scenes/` | [Scenes](../learn/scenes.md) |
| ECS resources | `examples/fundamentals/004_ecs/001_resources/app.py` | [Resources and feature composition](../learn/resources.md) |
| Entities/factories/components/queries/systems | `examples/fundamentals/004_ecs/` | [ECS](../learn/ecs.md), [Entities and components](../learn/entities-and-components.md), [Systems](../learn/systems.md) |
| Multiple scenes | `examples/fundamentals/005_multiple_scenes/app.py` | [Scenes](../learn/scenes.md) |
| Shared scene settings/resources | `examples/fundamentals/006_shared_scene_settings/app.py` | [Resources and feature composition](../learn/resources.md) |
| Transform | `examples/fundamentals/007_transform_component/app.py` | [Entities and components](../learn/entities-and-components.md) |
| Rect visual | `examples/fundamentals/008_visual_components/001_rect/app.py` | [Rendering](../learn/rendering.md), [Use visual components](../guides/use-visual-components.md) |
| Circle visual | `examples/fundamentals/008_visual_components/002_circle/app.py` | [Rendering](../learn/rendering.md) |
| Polygon visual | `examples/fundamentals/008_visual_components/003_polygon/app.py` | [Rendering](../learn/rendering.md) |
| Text visual | `examples/fundamentals/008_visual_components/004_text/app.py` | [Rendering](../learn/rendering.md) |
| Built-in visual rendering | `examples/fundamentals/009_rendering/001_render_system/app.py` | [Rendering](../learn/rendering.md) |
| Direct RenderQueue | `examples/fundamentals/009_rendering/002_render_queue/app.py` | [Use the render queue directly](../guides/use-render-queue.md) |
| Canvas | `examples/fundamentals/009_rendering/003_canvas/app.py` | [Rendering](../learn/rendering.md) |
| Layers and z-order | `examples/fundamentals/009_rendering/004_layers_and_z/app.py` | [Layers and z-order](../guides/layers-and-z-order.md) |
| Velocity integration | `examples/fundamentals/010_movement/001_velocity_integration/app.py` | [Movement](../learn/movement.md) |
| Desired movement | `examples/fundamentals/010_movement/002_movement_system/app.py` | [Movement](../learn/movement.md) |
| Controlled movement | `examples/fundamentals/010_movement/003_controlled_movement/app.py` | [Movement](../learn/movement.md) |
| Collision detection | `examples/fundamentals/011_collisions/001_detection/app.py` | [Collisions](../learn/collisions.md) |
| Collision response | `examples/fundamentals/011_collisions/002_response/app.py` | [Collisions](../learn/collisions.md), [Use collisions](../guides/use-collisions.md) |
| Collision sensors | `examples/fundamentals/011_collisions/003_sensors/app.py` | [Collisions](../learn/collisions.md) |
| Custom collision response | `examples/fundamentals/011_collisions/004_custom_response_rule/app.py` | [Collisions](../learn/collisions.md) |
| World bounds | `examples/fundamentals/012_bounds/001_behavior/app.py` | [Bounds](../learn/bounds.md), [Add world bounds](../guides/add-world-bounds.md) |
| Lifetime | `examples/fundamentals/013_lifecycle/001_lifetime/app.py` | [Spawning and lifecycle](../learn/spawning-and-lifecycle.md) |
| Respawn | `examples/fundamentals/013_lifecycle/002_respawn/app.py` | [Spawning and lifecycle](../learn/spawning-and-lifecycle.md) |
| Runtime spawn queue | `examples/fundamentals/013_lifecycle/003_runtime_spawn_queue/app.py` | [Spawning and lifecycle](../learn/spawning-and-lifecycle.md) |
| Particles | `examples/fundamentals/014_particles/app.py` | [Effects](../learn/effects.md), [Add particles](../guides/add-particles.md) |
| Trails | `examples/fundamentals/015_trails/app.py` | [Effects](../learn/effects.md), [Use trails](../guides/use-trails.md) |
| Camera effects | `examples/fundamentals/016_camera_effects/app.py` | [Effects](../learn/effects.md), [Use camera effects](../guides/use-camera-effects.md) |
| Screen effects | `examples/fundamentals/017_screen_effects/app.py` | [Effects](../learn/effects.md), [Use screen effects](../guides/use-screen-effects.md) |
| Game-facing audio | `examples/fundamentals/018_audio/app.py` | [Audio](../learn/audio.md), [Use audio](../guides/use-audio.md) |
| UI panel/layout | `examples/fundamentals/020_ui/001_panel_layout/app.py` | [UI](../learn/ui.md), [Use UI buttons and layout](../guides/use-ui-buttons-and-layout.md) |
| UI text | `examples/fundamentals/020_ui/002_text/app.py` | [UI](../learn/ui.md) |
| UI buttons/pointer interaction | `examples/fundamentals/020_ui/003_button/app.py` | [UI](../learn/ui.md) |

`001_backend` and `002_running` intentionally expose lower-level engine/platform APIs because those are the concepts they teach. Game-facing fundamentals from ECS/scene authoring onward should prefer Tatuy's public domain facades.

## Experiments

Experiments explore architecture, performance, and APIs under real pressure. They may intentionally use unfinished or internal APIs and are not automatically canonical authoring guidance.

## Games

Games demonstrate larger feature integration and should remain compatible with the engine behavior they intentionally exercise.

## Maintenance contract

Examples participate in validating Tatuy changes but are not pytest targets.

When engine behavior changes:

- review the nearest relevant fundamental
- review experiments using the affected capability
- review games using the affected capability
- add, update, or remove examples when necessary

Fundamentals should remain focused demonstrations of supported Tatuy APIs. Documentation should link to executable example source rather than reproducing entire files.

---
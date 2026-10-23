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

## Fundamentals

Teach one concept with minimal unrelated behavior. The supported progression is:

```text
001_backend/               low-level backend fundamentals
002_running/               low-level runtime/loop fundamentals
003_scenes/                scene basics
004_ecs/                   resources, entities, components, queries, systems
005_multiple_scenes/       scene transitions
006_shared_scene_settings/ shared settings/resources
007_transform_component/   world-space transforms
008_visual_components/     rect, circle, polygon, text
009_rendering/             RenderSystem, RenderQueue, Canvas, layers/z
010_movement/              velocity, desired movement, controls
011_collisions/            detection, response, sensors, custom rules
012_bounds/                clamp, bounce, wrap, despawn, side masks, border
013_lifecycle/             lifetime, respawn, runtime spawn queue
014_particles/             particle emission and processing
015_trails/                trail update and rendering
016_camera_effects/        camera shake
017_screen_effects/        screen flashes/effects
018_audio/                 game-facing SceneContext audio
020_ui/                    layout, text, buttons, pointer interaction
```

`001_backend` and `002_running` intentionally expose lower-level engine/platform APIs because those are the concepts they teach. Game-facing fundamentals from ECS/scene authoring onward should prefer Tatuy's public domain facades.

## Experiments

Explore architecture, performance, and APIs under real pressure.

## Games

Demonstrate larger feature integration.

Documentation should link to example source rather than reproducing entire example files.

## Maintenance contract

Examples participate in validating Tatuy changes but are not pytest test
targets.

When Tatuy engine behavior changes:

- review the nearest relevant fundamental
- review experiments using the affected capability
- review games using the affected capability
- add, update, or remove examples when necessary

Fundamentals should remain focused demonstrations of supported Tatuy APIs.

Experiments may intentionally pressure architecture or explore unfinished
ideas and are not automatically canonical API guidance.

Games demonstrate larger integration and should remain compatible with the
engine behavior they intentionally exercise.

---

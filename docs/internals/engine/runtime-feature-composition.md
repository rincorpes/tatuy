# Runtime Feature Composition Internals

This page is for contributors changing Tatuy's default scene/runtime composition.

Canonical architecture: [Feature Composition](../../architecture/feature-composition.md).

## Primary source

```text
src/tatuy/engine/runtime/
├── scene_composition.py
├── builtins.py
└── bootstrap.py
```

Related source:

```text
src/tatuy/engine/pipelines.py
src/tatuy/engine/system.py
src/tatuy/scenes/scene.py
```

## `DefaultSceneInitializer`

`DefaultSceneInitializer` converts Scene declarations into runtime state before `Scene.on_enter()`.

When adding default provisioning, ask:

1. Is this truly runtime composition policy rather than feature behavior?
2. Does the feature already own the resource/component type?
3. Can the Scene express intent declaratively instead of constructing runtime plumbing itself?
4. Will custom `SceneService` users retain their current opt-in behavior?

Do not turn `Scene.configure()` into a feature bootstrap registry.

## `BuiltinSystemCatalog`

`BuiltinSystemCatalog` owns default built-in installation, activation, phase, and order.

Activation predicates should remain cheap and coarse. They may check required resources or whether relevant entity/component combinations exist. They should not duplicate the system/kernel's detailed validation or behavior.

When adding or moving a built-in:

- choose the semantic phase first
- use order only for dependencies inside that phase
- add/update focused activation/order tests
- update `docs/architecture/system-pipeline.md`
- update relevant fundamentals if author-visible behavior changes

## `SystemPipelineFactory`

The pipeline factory merges:

1. catalog registrations
2. Scene `builtin_overrides()`
3. `scene.systems`
4. `scene.game_systems(ctx)`

Unknown built-in override names are errors. A `None` override removes the default built-in registration.

Do not bypass this composition path by installing default systems directly from Scene code.

## Structural committers

Default structural commit composition coordinates generic ECS structural commands and lifecycle commits at barriers.

Keep structural mutation timing explicit. Do not move entity-set mutations into arbitrary simulation systems merely to simplify local code.

## Contributor checklist

For a runtime-composition change:

- feature meaning remains owned by the feature package
- Scene remains declarative
- default runtime behavior is covered by activation/order tests
- custom runtime composition remains possible
- public game imports do not gain runtime-internal dependencies
- docs and fundamentals reflect any visible contract change

---
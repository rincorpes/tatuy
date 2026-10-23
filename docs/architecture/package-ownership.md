# Package Ownership and Dependency Direction

Tatuy's package structure is organized so game-facing features depend on lower-level primitives, while runtime composition depends inward on the concrete features it assembles. Lower-level packages must not import higher-level feature implementations.

## Dependency direction

The intended dependency direction is approximately:

```text
math
  ↓
geometry
  ↓
ECS primitives / graphics primitives
  ↓
features
  ↓
scenes / authoring abstractions
  ↓
runtime composition
```

Rendering and platform execution remain directional:

```text
game / features
      ↓
semantic render data
      ↓
render executor
      ↓
backend / platform
```

Tooling is outside the required runtime path:

```text
profiler tooling
MCP
capture/video tooling
editor tooling
export/build tooling
```

Tooling may depend on runtime concepts, but runtime code must not require tooling infrastructure merely to function.

## Ownership rules

### `tatuy.math`

Owns mathematical value types and operations. It must not depend on Tatuy features, scenes, runtime composition, backends, or tooling.

### `tatuy.geometry`

Owns backend-agnostic spatial geometry, queries, and geometric algorithms. It may depend on `tatuy.math`, but it must not depend on feature implementations.

### `tatuy.ecs`

Owns generic ECS primitives, storage contracts, entity construction primitives, structural commands, worlds, queries, and system contracts. It must remain feature-agnostic.

Feature-specific blueprints, resources, components, and policy belong to their owning features rather than ECS.

### `tatuy.graphics`

Owns low-level rendering and view primitives: colors, canvas contracts, viewport/view transforms, semantic render commands, render packets, render queues, executor contracts, and related backend-agnostic presentation data.

`tatuy.graphics` must not import concrete feature implementations. Presentation helpers that know about a concrete feature belong to that feature and may depend downward on `tatuy.graphics`.

For example, world-bounds border rendering belongs to `tatuy.features.bounds`, because it consumes `WorldBoundsBorder`, even though it emits generic render commands.

### `tatuy.features`

Owns reusable optional game behavior and its feature-specific components, resources, systems, kernels, presentation helpers, and construction policy.

Features may depend on ECS, geometry, math, and public graphics primitives. A feature should not depend on unrelated feature implementations unless that relationship is explicit and intentional.

Feature-specific rendering should emit semantic render data through `tatuy.graphics`; graphics must not depend back on the feature.

### `tatuy.scenes`

Owns the game-authoring scene abstraction, scene lifecycle, scene context, and declarations that are intentionally part of the authoring contract.

Scenes may consume public feature contracts, but generic Scene code should not become the ownership location for optional feature implementation or bootstrap policy. Default optional-feature provisioning belongs to runtime composition unless an authoring convenience is deliberately made part of the Scene contract.

### `tatuy.engine.runtime`

Owns default built-in composition: which built-in features are installed, their activation rules, and their default ordering.

Runtime composition is intentionally allowed to depend on concrete built-in features because composition is its responsibility. This is the dependency root, not a lower-level reusable primitive.

### `tatuy.backend`

Owns platform/backend execution contracts and concrete backend implementations. Backend/platform modules must not import game features.

Feature and render code communicate with backends through lower-level contracts and semantic data rather than feature-specific backend knowledge.

### `tatuy.tooling` and MCP/editor/export tooling

Own development-time or optional operational tooling. These packages may depend inward on engine/runtime concepts, but the core game runtime must not require them simply to import or execute.

## Feature presentation rule

When code renders a concrete feature concept, ownership follows the feature data it understands.

```text
feature resource/component
        ↓
feature presentation helper/system
        ↓
graphics render primitives / RenderQueue
```

Do not place the presentation helper under `graphics` merely because its final operation is drawing.

This rule removed the previous conceptual cycle:

```text
features.bounds.systems
        ↓
graphics.bounds_border
        ↓
features.bounds.resources
```

The renderer now belongs to `features.bounds`, so dependency direction is one-way:

```text
features.bounds
        ↓
graphics.render
```

## Effects ownership

`ViewTransform` remains a graphics/view primitive because it is semantic view data.

Camera shake policy (`CameraFX`) and screen-effect state/policy (`ScreenEffectStack`, `ScreenEffect`, `FlashEffect`) are owned by `tatuy.features.fx` because they are optional reusable game/presentation behavior rather than low-level render infrastructure.

`CameraFX` depends downward on the graphics-owned `ViewTransform` value. Screen effects depend downward on `Color` and low-level `ScreenOverlay` render data. The dependency therefore remains one-way: feature policy produces graphics primitives, while `tatuy.graphics` has no knowledge of the FX feature.

## UI ownership

UI and visual presentation must not depend on each other cyclically. The visual feature must not know that UI exists. UI should render independently into semantic render data.

Whether UI remains a top-level subsystem or becomes `features.ui` is a separate ownership decision; whichever choice is made must preserve one-way dependencies and be documented explicitly.

## Prohibited directions

At minimum, these dependency directions are prohibited:

- `math -> features`
- `geometry -> features`
- `ecs -> features`
- `graphics -> concrete feature implementations`
- `backend -> game features`
- core runtime primitives -> MCP/editor/export tooling
- feature A -> unrelated feature B without an explicit composition contract

## Placement test for new code

Before adding a type, answer these questions:

1. Which domain concept does the type understand directly?
2. Is that concept a low-level primitive, a reusable game feature, an authoring abstraction, composition policy, platform execution, or tooling?
3. Which lower-level packages does it need?
4. Would placing it there force a lower-level package to import a higher-level one?
5. Could a future native implementation replace the lower-level implementation without moving the game-facing boundary?

If the answers are ambiguous, ownership should be resolved before adding another cross-package dependency.

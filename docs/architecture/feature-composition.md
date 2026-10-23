# Feature Composition

Tatuy keeps reusable feature behavior separate from the runtime policy that decides which built-ins are installed for a scene.

## Responsibilities

Game-facing feature packages own their own components, resources, systems, kernels, and presentation helpers.

Examples:

```text
features.movement
features.bounds
features.collision
features.lifecycle
features.fx
features.visual
ui
```

They do not decide globally when Tatuy should install or schedule them.

Default composition belongs to `tatuy.engine.runtime`.

## Scene declarations versus runtime provisioning

A `Scene` declares what it wants through authoring hooks such as:

```python
def resources(self, ctx): ...
def spawn_definitions(self, ctx): ...
def entities(self, ctx): ...
def bounds(self, ctx): ...
def bounds_border(self, ctx): ...
def game_systems(self, ctx): ...
def builtin_overrides(self, ctx): ...
```

The scene does not bootstrap optional feature implementations itself.

`DefaultSceneInitializer` interprets those declarations and provisions default runtime-owned state before `Scene.on_enter()` runs.

That includes:

- shared application resources
- scene-declared resources
- the structural command buffer
- lifecycle queue and spawn registry
- declared spawn definitions and initial entity placements
- world-bounds resources
- camera and screen-effect services

This keeps `Scene` as an authoring abstraction instead of a feature manager.

## Built-in systems

`BuiltinSystemCatalog` defines the default built-in systems, their activation predicates, and their scheduling metadata.

Activation is deliberately coarse. A predicate answers only whether a system has plausible work to do, for example:

- required resources exist
- at least one relevant component combination exists
- a frame resource contains events to process

The feature system or kernel still owns detailed validation and behavior.

See [System Pipeline Architecture](system-pipeline.md) for the exact phase/order contract.

## Ownership direction

```text
game / Scene declarations
        ↓
engine.runtime composition
        ↓
feature systems and resources
        ↓
ECS / geometry / graphics primitives
```

Runtime composition may depend on concrete built-ins because composition is its responsibility. Lower-level packages must not depend back on runtime composition.

## Scene responsibilities

A normal game scene should:

- declare its world, intent, and tick-context types
- declare resources and feature configuration
- declare spawn definitions and initial placements
- provide game-specific systems
- implement lifecycle hooks such as `on_enter()` and `on_exit()`

A normal game scene should not:

- manually recreate Tatuy's default runtime bootstrap
- install render executors or compilers
- know ECS storage implementation details
- depend on backend-specific rendering objects
- duplicate built-in feature activation logic

## Native replacement contract

Future native implementations may replace hot kernels, storage, render execution, or other implementation details, but they must preserve the authoring-visible behavior of composition:

- the same Scene declarations remain valid
- default feature resources appear at the same lifecycle point
- built-in activation and phase/order guarantees remain observable
- `game_systems()` and `builtin_overrides()` keep their meaning
- Python-defined game components/resources remain usable

If a native migration requires normal scenes to understand the native implementation, the boundary is too low-level.

---
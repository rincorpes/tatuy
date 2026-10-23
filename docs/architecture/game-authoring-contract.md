# Game Authoring Contract

Tatuy games are authored in Python against a stable engine-facing API. Engine internals may move between Python, native code, SDL, WebAssembly, or other implementations without requiring normal game code to change.

## Purpose

This document defines the boundary between game-authoring APIs and implementation details.

The rule is simple:

> Game code should depend on Tatuy concepts, not on the current implementation of those concepts.

This contract is intentionally narrower than the complete engine API. Engine-internals examples may teach backend, runtime, rendering, or storage internals, but normal games should not depend on those internals.

## Authoring layer

Game code may depend on stable concepts such as:

- `TatuyApp`
- `Scene` and scene registration/policy APIs
- `Intent` and scene/game contexts
- `GameSystem`
- selected reusable system extension points where explicitly supported
- `World` as the ECS facade
- `EntityId`
- public component/resource APIs
- entity blueprints and spawn APIs
- structural/game commands
- input abstractions
- geometry and math primitives
- public rendering/canvas abstractions
- game audio abstractions
- settings/configuration APIs intended for game use

The canonical import strategy is domain-oriented rather than root-flattened. Normal game code should prefer:

```python
from tatuy import TatuyApp
from tatuy.ecs import World, GameSystem, EntityFactory
from tatuy.engine import SystemRegistration
from tatuy.scenes import Scene, Intent, SceneRegistry, SceneTickContext
from tatuy.features.movement import Movement, Velocity
from tatuy.features.collision import CollisionFrame, ColliderAccess
from tatuy.features.visual import Rect, RectBlueprint
from tatuy.ui import UiNode
```

The root `tatuy` package intentionally remains small. Domain facades expose stable authoring concepts and supported extension points; implementation modules remain deep. Examples and games should teach the facade path unless the example is explicitly about the internal implementation.

## Internal implementation layer

Normal game code should not depend directly on implementation-sensitive modules such as:

- runtime composition/bootstrap internals
- concrete backend implementation classes such as Pygame-specific runtime objects
- future SDL implementation classes
- render compiler/executor/pipeline internals
- ECS storage representation
- native binding implementation details
- feature activation/bootstrap plumbing
- platform-specific handles or ABI types

These areas may be documented for engine contributors and may appear in fundamentals that explicitly teach engine internals.

## Fundamentals versus games

`examples/fundamentals` has two roles:

1. teach public game-authoring APIs
2. teach engine/backend internals when the example is explicitly about those internals

Therefore a backend fundamental may legitimately import `tatuy.backend.pygame.*`, while a normal game should not use that import merely because the fundamental does.

`examples/games` and gameplay-oriented experiments are stronger evidence for the desired authoring surface.

`examples/experiments/002_entities` is treated as a representative high-pressure gameplay case because it exercises the engine in a Shatterphase-like way.

## Native boundary rule

Native boundaries must be coarse-grained.

Preferred:

```text
Python game/system orchestration
    -> one engine/native operation
        -> process many entities, collisions, or draw commands
    -> return
```

Avoid designs that cross Python/native boundaries per entity, component, collider, or draw command.

A native migration should replace an implementation behind an existing engine-facing abstraction rather than introducing native concepts into game code.

## ECS contract

`World` is the game-facing ECS facade.

Its current storage representation is not part of the public contract.

Game code may conceptually rely on operations such as:

```python
entity = world.create_entity()
world.add_component(entity, component)
component = world.get_component(entity, ComponentType)

for entity, transform, velocity in world.query(Transform, Velocity):
    ...
```

The implementation behind those operations must remain replaceable.

The intended direction is:

```text
World
  -> ECSStore
      -> PythonECSStore
      -> future NativeECSStore
```

Arbitrary Python-defined components must remain supported. Native-known components may gain optimized storage later, but user-defined Python components must not be excluded by the native architecture.

## System contract

`GameSystem` remains part of the Python authoring layer.

Tatuy should not move the scheduler to native code merely because other hot paths become native. Scheduling a relatively small number of coarse operations can remain in Python unless profiling proves otherwise.

Built-in systems may become thin wrappers around replaceable kernels. For example:

```text
VelocityIntegrationSystem
  -> MovementKernel
      -> PythonMovementKernel
      -> future NativeMovementKernel
```

Game code should not need to know which implementation is active.

## Rendering contract

Game code should depend on semantic rendering APIs, not backend draw calls or native ABI objects.

Typed render commands, ordering/layer semantics, camera/view information, and supported canvas APIs are part of the intended engine-facing model.

The internal command buffer and executor may later move to contiguous native memory without changing the game-facing rendering API.

Explicit Python fallback commands may remain available as an escape hatch, but they should not become the representation for normal rendering.

## Platform contract

The engine runtime must remain host-agnostic.

Desktop and browser hosts may drive the same engine session differently:

```text
Desktop host -> loop -> engine.step(...)
Browser host -> browser scheduler -> engine.step(...)
```

Browser support must not be implemented as scattered `if web` branches inside the engine core.

Platform-specific concerns such as windowing, events, input, graphics device, audio, assets, and persistent storage belong behind platform/runtime capabilities.

## Public API migration rules

When establishing or changing the authoring surface:

1. inspect fundamentals, experiments, and games before choosing the boundary
2. prefer canonical public imports over deep implementation imports
3. do not preserve a poor boundary only because an old example imports it
4. update examples gradually when a canonical path is established
5. keep implementation-only modules available to engine contributors without presenting them as normal game API
6. do not flatten every symbol into `tatuy.__init__` only to make imports shorter
7. favor stable domain-level modules and facades

## Current audit observations

The current examples show several categories of usage:

- backend fundamentals intentionally import Pygame-specific implementation classes
- runtime fundamentals intentionally access engine/runtime internals
- games primarily use `TatuyApp`, ECS concepts, features, scenes, geometry, input, and rendering-facing types
- gameplay experiments, especially `002_entities`, exercise deeper feature resources/systems and are useful for identifying where the current public surface is still too implementation-oriented

This audit is evidence for refining canonical imports; it is not a declaration that every currently imported deep module is public API.

## First implementation target

The first structural implementation following this contract is the ECS storage boundary.

The initial change should:

1. introduce an `ECSStore`-like contract
2. move current dict-based ECS storage behind a `PythonECSStore`
3. keep `World` as the facade
4. preserve existing behavior
5. add store conformance tests
6. avoid C++ in the first extraction
7. preserve arbitrary Python-defined components

Only after this boundary is proven should a native store prototype be considered.

## Compatibility test

For future architecture decisions, use this question:

> If this implementation moved from Python to C++ tomorrow, would normal game code have to change?

If the answer is yes, the boundary is probably exposing implementation details and should be reviewed.

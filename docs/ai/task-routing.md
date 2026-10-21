# Task Routing

Use the request to determine where to inspect first.

## Player / enemy / wave / score / boss rule

Start in the game.

Do not begin by modifying Tatuy.

## Movement behavior

Inspect:

```text
game system
features/movement
features/spatial
```

## Collision behavior

Inspect:

```text
game collision rules
features/collision
built-in collision ordering
```

## Entity creation/lifetime

Inspect:

```text
Scene.spawn_definitions
LifecycleQueue
features/lifecycle
EntityFactory
```

## Slow frame

Inspect:

```text
profile
dominant span
relevant system/feature
```

Do not propose C++ first.

## Rendering problem

Inspect:

```text
game presentation
graphics/
engine/render/
backend renderer
```

in that order.

## Pygame-specific issue

Inspect backend implementation.

## Scene ordering/input issue

Inspect:

```text
ScenePolicy
SceneService
engine/scene.py
```

## New reusable feature

Inspect:

1. nearest existing feature
2. nearby fundamental example
3. game requirement
4. whether the feature actually generalizes

---

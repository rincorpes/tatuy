# Dependency Constraints

This page is a contributor checklist for package boundaries. The canonical architectural rationale lives in [Package Ownership and Dependency Direction](../architecture/package-ownership.md).

## Allowed direction

```text
math
  ↓
geometry
  ↓
ECS / graphics primitives
  ↓
features
  ↓
scenes / authoring abstractions
  ↓
runtime composition
```

Platform execution continues downward from semantic rendering into executors/backends.

Tooling may depend inward on runtime concepts, but normal runtime imports must not require tooling infrastructure.

## Prohibited directions

Do not introduce:

- `math -> features`
- `geometry -> features`
- `ecs -> concrete features`
- `graphics -> concrete feature implementations`
- `backend -> game features`
- core runtime primitives -> MCP/editor/export tooling
- unrelated feature-to-feature coupling without an explicit composition contract

## Placement test

Before adding a module or moving a type, ask:

1. Which domain concept does it understand?
2. Is it a primitive, reusable feature, authoring abstraction, runtime policy, platform implementation, or tooling?
3. Which lower-level packages does it need?
4. Would this placement make a lower-level package import a higher-level implementation?
5. Could the implementation move to native code without moving the game-facing API?

If the answer to question 4 is yes, stop and revisit ownership.

## Presentation helpers

A helper that understands feature-specific data belongs to the feature even if its final output is rendering.

```text
feature component/resource
        ↓
feature presentation helper
        ↓
graphics semantic data
```

Do not move it under `graphics` merely because it draws.

## Runtime composition exception

`tatuy.engine.runtime` is intentionally allowed to depend on concrete built-ins because composition is its responsibility. This exception does not make it acceptable for lower-level generic engine/ECS/graphics code to import those features.

## Review checklist

For structural changes:

- search imports in both directions
- check public facades for accidental implementation leakage
- inspect examples/games for new deep imports
- update package-ownership docs when the boundary itself changes
- add dependency tests/lint rules if a recurring violation becomes easy to automate

---
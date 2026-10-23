# ECS Architecture

Tatuy's ECS exists to make composition explicit.

## Entity

Identity only.

## Components

Per-entity state.

## Resources

Per-world state.

## Systems

Behavior over state combinations.

## Structural boundary

Structural changes are synchronized rather than applied arbitrarily during system iteration.

## Storage boundary

`World` is the game-facing ECS facade. Entity identity and component persistence are delegated to an `ECSStore` implementation.

The default `PythonECSStore` preserves the current Python-container behavior and acts as the reference implementation. Future native storage must conform to the same observable `World` behavior rather than becoming a new game-facing API.

Resources remain owned by `World`; they are not part of the ECS storage migration yet.

## Query strategy

`World.query()` delegates query execution to `ECSStore.query()` using the selected strategy name. The store owns the storage-specific iteration required to produce query rows.

Python query strategies remain selectable by name, but raw component mappings are now an implementation detail of `PythonECSStore` rather than part of the `World.query()` contract.

Games should normally keep the default strategy unless profiling demonstrates a reason to change it.

---

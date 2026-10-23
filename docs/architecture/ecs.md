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

Query strategy objects are storage-independent selectors: they provide a strategy name, while the active `ECSStore` owns the corresponding execution. Raw component mappings are no longer part of the query contract.

Games should normally keep the default strategy unless profiling demonstrates a reason to change it.

## Entity construction boundary

`EntityFactory` and the generic blueprint lifecycle live under `tatuy.ecs.entity` and depend only on world/entity/component operations. They do not own concrete visual, spatial, or collision feature policy.

Built-in shape blueprints live with the visual feature in `tatuy.features.visual.blueprints`. Optional collider/body construction is owned by `tatuy.features.collision.blueprints`.

This keeps the generic entity-construction path compatible with both the current Python store and a future native-backed store while allowing feature-owned convenience blueprints to compose normal public components.

---

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

## Query strategy

The world delegates query selection to a strategy.

This keeps query/storage experimentation from becoming a gameplay API concern.

Games should normally keep the default strategy unless profiling demonstrates a reason to change it.

---

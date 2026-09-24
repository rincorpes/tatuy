# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]

## - 2026-09-24

### Added

- Implement movement system with velocity calculation and desired movement handling
- Direction systems for collisions and bounds

### Changed

- Update MovementControls integration in movement systems
- Reorganize imports and update WorldBoundsBorder class definition
- Clean up import statements in lifecycle and bounds systems

## - 2026-09-23

### Added

- Enhance Vec2 operations to support scalar addition and subtraction

### Changed

- Update entity factory import path for consistency
- Update built-in components, resources and systems import paths as features
- Introduce UI components and resources for enhanced interface management

## - 2026-09-22

### Added

- **Tatuy Core & Architecture:** Added base `Engine`, `Runtime`, `TatuyApp` entry point, and internal resource store with a Python-based main loop.
- **ECS (Entity Component System):** Implemented `World` store, entity factory, base systems pipeline, and built-in systems (Physics, Collision, Movement, Lifetime, UI Layout).
- **Backend Protocol & Pygame:** Introduced backend abstractions (`Window`, `Input`, `Audio`, `Events`) with a fully featured Pygame implementation.
- **Graphics & Rendering:** Added a generic `Render Queue`, `Render Pipeline`, and viewport transformations (clipping, shapes, text, textures).
- **Scene Management:** Added `Scene Context`, `Scene Registry`, and engine-integrated lifecycle ticks (`update`, `present`).
- **Capture & Replay System:** Built a custom replay recorder/player with background workers and video encoding capabilities.
- **Tatuy CLI:** Created a command-line interface to run internal examples, experiments, and games.
- **Documentation & Examples:** Added comprehensive architectural docs and interactive fundamental examples for every core module.

### Fix

- Update pixel format from ``argb8888`` to ``bgra8888`` in capture functionality

### Change

- Replace BaseWorld with World in multiple files
- Rename BaseIntent to Intent for consistency across context and UI
- Rename BaseTickContext to SceneTickContext for improved clarity and consistency
- Change scene world and intent to composition introducing types and cache

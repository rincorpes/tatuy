# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]

### - 2026-10-08

#### Added

- Implement lifecycle management with LifecycleCommitter and associated systems; add spawn and despawn handling
- Enhance lifecycle management with dynamic kwargs handling in SpawnRequest and add EntitySpawn class for improved spawn definition management
- Introduce movement and bounds systems; enhance scene management with resource handling and diagnostics

#### Changed

- Refactor engine and scene systems; introduce structural command system and built-in system catalog

## - [0.1.0] 2026-09-30

First public alpha release

### - 2026-09-29

#### Added

- Implement match_contact function for collision detection between entities
- Add rotation and dot product methods to Vec2 class
- Add MotionSample component and integrate it into KinematicVelocitySystem
- Implement particle effects with ParticleEmitter, components, and systems
- Add dataclass_from_dict utility for converting dictionaries to dataclass instances
- Implement screen effects system with ScreenEffectStack and FlashEffect
- Add camera effects system with CameraFX and integrate into Scene

#### Changed

- Update import statements for visual components in factory and render modules

### - 2026-09-28

#### Added

- Circle and Text blueprints with attributes for entity creation
- Add AttachmentSystem to manage entity attachments and position updates

#### Changed

- Make blueprints reusable and composable.
- Remove Paddle and PaddleMotionSample classes from component and system modules
- Restructure collision and visual components, removing obsolete files and introducing new collider access and velocity rule classes

### - 2026-09-25

#### Added

- Implement resource management methods in World class
- Implementation based registry for entity factory
- Introduce Base blueprint for rectangles
- Enhance entity creation with identity building in EntityBlueprint

#### Changed

- Enhance entity creation in EntityFactory and RectBlueprint with optional entity parameter
- Move entity creation logic to build method in RectBlueprint
- Entity creation in blue print moved to the base blueprint class

### - 2026-09-24

#### Added

- Implement movement system with velocity calculation and desired movement handling
- Direction systems for collisions and bounds
- Add debug overlay pass for FPS display and integrate into render pipeline

#### Changed

- Update MovementControls integration in movement systems
- Reorganize imports and update WorldBoundsBorder class definition
- Clean up import statements in lifecycle and bounds systems
- Update Movement class acceleration type and simplify velocity calculation in MovementMotor

### - 2026-09-23

#### Added

- Enhance Vec2 operations to support scalar addition and subtraction

#### Changed

- Update entity factory import path for consistency
- Update built-in components, resources and systems import paths as features
- Introduce UI components and resources for enhanced interface management

### - 2026-09-22

#### Added

- **Tatuy Core & Architecture:** Added base `Engine`, `Runtime`, `TatuyApp` entry point, and internal resource store with a Python-based main loop.
- **ECS (Entity Component System):** Implemented `World` store, entity factory, base systems pipeline, and built-in systems (Physics, Collision, Movement, Lifetime, UI Layout).
- **Backend Protocol & Pygame:** Introduced backend abstractions (`Window`, `Input`, `Audio`, `Events`) with a fully featured Pygame implementation.
- **Graphics & Rendering:** Added a generic `Render Queue`, `Render Pipeline`, and viewport transformations (clipping, shapes, text, textures).
- **Scene Management:** Added `Scene Context`, `Scene Registry`, and engine-integrated lifecycle ticks (`update`, `present`).
- **Capture & Replay System:** Built a custom replay recorder/player with background workers and video encoding capabilities.
- **Tatuy CLI:** Created a command-line interface to run internal examples, experiments, and games.
- **Documentation & Examples:** Added comprehensive architectural docs and interactive fundamental examples for every core module.

#### Fix

- Update pixel format from ``argb8888`` to ``bgra8888`` in capture functionality

#### Change

- Replace BaseWorld with World in multiple files
- Rename BaseIntent to Intent for consistency across context and UI
- Rename BaseTickContext to SceneTickContext for improved clarity and consistency
- Change scene world and intent to composition introducing types and cache

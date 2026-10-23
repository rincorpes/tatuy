# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]

### - 2026-10-23

#### Added

- Add Game Authoring Contract documentation and update API map references
- Introduce ECS storage and query strategies with Python implementation
- Implement movement calculation and velocity integration kernels with corresponding tests
- Introduce bounds and spatial kernels for performance-sensitive operations with corresponding tests
- Implement collision detection kernel and related tests for performance-sensitive operations
- Implement collision response kernel and corresponding tests for batch contact resolution
- Add lifecycle commit kernel and corresponding tests for structural mutation
- Add particle processing kernel and system with corresponding tests for FX features
- Implement BoundsBorderRenderer and corresponding tests for bounds feature

#### Changed

- Moved PythonLoop and related runtime loop components to a new runtime loop module.
- Introduced FrameClock for managing frame timing in the runtime loop.
- Added ScenePresenter and SceneUpdater for handling scene presentation and updates.
- Created CaptureInputProcessor for managing input capture and replay.
- Implemented FrameRenderer for coordinating frame rendering and capture.
- Established contracts for rendering operations with RenderExecutor and PythonRenderExecutor.
- Added built-in system registrations and activation predicates for scene systems.
- Updated tests to cover new runtime and rendering functionalities, ensuring proper execution and cleanup.
- Removed obsolete test files and refactored existing tests to align with new architecture.
- Add MCPContext to manage configuration, projects, paths, files, and execution components.
- Introduce CommandRunner for executing commands with timeout and output management.
- Implement PythonAnalyzer for running mypy and pylint analysis on projects.
- Create PythonFormatter for formatting Python files using isort and black.
- Develop TestRunner for executing pytest tests within projects.
- Establish ProjectRegistry for managing project entries and discovery.
- Implement WorkspaceFiles for file operations within the workspace.
- Create WorkspaceSearch for searching text within project files.
- Add TatuyScaffolding for creating new project targets.
- Register tools for file management, project listing, and verification in the MCP server.
- Add tests for access policy and server creation functionality.
- Update query strategy implementation for storage independence and clean up unused code
- Change entity blueprints and factories for enhanced entity construction and management

### - 2026-10-22

#### Added

- Implement file creation and editing tools with path validation and access checks
- Add tools for static validation, code formatting and tests to the MCP server.

#### Changed

- Refactor verification and development documentation; enhance server functionality
- Refactor backend lifecycle documentation and enhance test coverage
- Update documentation and improve verification guidance; enhance MCP server functionality
- Enhance Pygame backend initialization and cleanup; implement rollback on failures
- Ensure audio operations are no-ops when disabled or mixer is uninitialized; enhance tests for robustness
- Retain normalized master volume for later sound loads; enhance volume handling and tests
- Update capture functionality to accept optional path; enhance tests for error propagation and default behavior
- Update translucent polygon rendering to include extreme vertex pixels; enhance tests for alpha coverage
- Update tiled texture handling to apply viewport transformations; enhance tests for cropping and clipping behavior
- Simplify font path resolution logic; enhance tests for font selection and error propagation
- Moved engine start to the main loop for better control flow.
- Added deprecation warnings for unused capture configurations in AudioConfig.
- Introduced sync_size method in PygameWindow to handle native resize notifications.
- Enhanced PygameEvents to support keyboard and mouse enabling/disabling via InputConfig.
- Updated PygameInput to raise NotImplementedError for unsupported gamepad input.
- Improved error handling for invalid texture geometry and shape sizes in PygameRenderer.
- Added support for customizable screenshot formats in CaptureSettings and CaptureWorker.
- Implemented tests for new input handling features and capture settings.
- Removed obsolete sample test file and added new tests for input and window services.
- Enhance engine cleanup process with retry logic and error propagation
- Update texture handling to enforce C-contiguous memoryviews and enhance related tests
- Update backend configuration to expose read-only properties for capability settings

### - 2026-10-21

#### Added

- Add comprehensive documentation for Tatuy engine internals and features
- Implement create command operation with input handling and scaffolding
- Enhance project management with dynamic project discovery and target creation

### - 2026-10-20

#### Added

- Add AGENTS.md and SKILL.md for repository guidance and development collaboration

#### Changed

- Revise README.md for clarity and detail on engine architecture and features

### - 2026-10-19

#### Added

- Integrate profiler spans in bounds and lifecycle systems for performance tracking
- Enhance profiling in entity creation and lifecycle spawning processes
- Introduce query strategies for improved entity querying in World and Scene classes
- Add Tatuy MCP server for ChatGPT integration
- Add Tatuy Profiler module with server and viewer components

### - 2026-10-16

#### Added

- Add ParticleEmitResult dataclass and enhance ParticleEmitter with available property

### - 2026-10-15

#### Added

- Integrate profiling enhancements; add span tracking in SceneUpdater and SystemRegistration, and extend Profiler with metrics and annotations
- Add profiling viewer; implement profile export, snapshot handling, and web interface for visualization
- Improve garbage collection handling and enhance profiler data structures
- Integrate profiler spans for rendering frame operations in PygameRenderer and RenderPipeline
- Enhance collision detection with profiling spans for collider collection and pair testing

### - 2026-10-14

#### Added

- Integrate profiling system; add profiler configuration and span tracking across event handling and engine lifecycle
- Enhance profiling capabilities; add granular profiling spans and GC event tracking
- Enhance profiler functionality; add RunStats for detailed run metrics and optimize root management with deque

### - 2026-10-09

#### Added

- Implement collision system enhancements; add polygon collider support and improve collision detection mechanisms
- Add attachment system and activation; implement attachment handling in spatial systems

#### Changed

- Update system registration order for attachment and collision systems; streamline activation management

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

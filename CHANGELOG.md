# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]

### - 2026-10-28

#### Added

- Add gesture-gated runtime audio readiness with deferred sound loads, mute state, visible unlock errors, and user-input activation through the normal Tatuy input frame.
- Add declarative `web_package.files` support so browser targets can stage repository assets outside their source directory and include those files in deterministic build fingerprints.
- Add logical viewport resize mapping so host-window changes preserve game resolution, center/scale the rendered viewport, and map pointer input back into game coordinates.
- Add Playwright browser smoke coverage, automated showcase thumbnails, manual Chromium/Firefox/WebKit diagnostics, and representative browser performance reporting.
- Add per-target and site build provenance with commit, Tatuy/Pygbag/MkDocs/Python versions, target build fingerprints, and Poetry lockfile hashing.
- Add optional showcase metadata generation to game/experiment scaffolding across the CLI and Tatuy Development MCP paths.

#### Changed

- Promote the four representative W12 browser-input fundamentals to public browser playables after successful Chromium smoke verification of focus, keyboard, pointer, scene-transition, and scroll-suppression behavior.
- Preserve each browser target's audio enablement while forcing deferred `auto_init: false`, and prepare the game-facing audio fundamental for browser verification with packaged audio plus `SPACE`/`M` controls.
- Verify Chromium audio unlock, repeated playback, and mute/unmute behavior; keep strict Pygbag sound-format validation as the default while exposing an explicit local-smoke override for the temporary WAV asset until it is replaced by OGG.
- Keep showcase game-space independent from browser/CSS dimensions by using logical viewport sizes in fundamentals and a responsive/fullscreen runtime wrapper; verify resize, letterboxing, pointer alignment, fullscreen entry/exit, and unchanged gameplay behavior in Chromium.
- Make generated showcase output safe for GitHub Project Pages by keeping internal links relative, validating HTML/CSS against root-absolute internal URLs, and testing representative navigation beneath the canonical `/tatuy/` path.
- Add a metadata-driven GitHub Pages workflow that validates showcase declarations, builds all browser-enabled targets and strict docs, validates the composed static output, uploads `build/web`, and deploys from `main` while keeping pull requests build-only.
- Add a shared showcase build orchestrator with `--serve` local preview so local and GitHub Actions publication paths use the same metadata, browser-target, docs, shell, and validation stages.
- Fix strict MkDocs publication by removing stale `reference/` links and using canonical GitHub URLs for contributor-only `AGENTS.md` links outside the docs tree.
- Allow canonical `/tatuy/...` root URLs produced by MkDocs while continuing to reject root-absolute links that escape the GitHub Project Pages base path.
- Configure GitHub Pages only in the deployment job so pull-request/build validation does not require a pre-existing Pages site; document the one-time repository setting to use GitHub Actions as the Pages source.
- Verify the hosted GitHub Actions deployment and live `https://rincorpes.github.io/tatuy/` showcase, including a browser-playable controlled-movement target under the real `/tatuy/` project path.
- Promote Snake, Procedural Tree, and Infection Arena as the first non-fundamental browser targets while classifying the remaining active games/experiments with explicit pending or V0-excluded status.
- Group showcase cards into Fundamentals, Games, and Experiments; add loading/failure UX, sandboxed runtime iframes, build metadata, metadata-driven docs/live-demo links, and private-file publication guards.
- Pin the Pages bootstrap Poetry version and record publication toolchain metadata so browser builds are traceable to the producing checkout and lockfile.

### - 2026-10-27

#### Added

- Add explicit synchronous and asynchronous runtime hosts so application composition is independent from host execution semantics.
- Add layered YAML configuration loading with deterministic recursive mapping merges and profile overlays.
- Add a `web` configuration profile for the canonical render-queue fundamental and tests for layered configuration precedence.
- Add an independent replay runtime capability with enabled and null services so deterministic replay no longer depends on screenshot/video capture.
- Add a read-only `AssetProvider` boundary with a filesystem-backed implementation exposed to scenes through `ctx.assets`.
- Add logical `StorageProvider` abstractions with filesystem-backed desktop persistence and ephemeral in-memory storage exposed through `ctx.storage`.
- Add reusable web-target packaging models and a `WebTargetBuilder`/`PygbagPackager` tooling boundary for browser builds and showcase metadata.
- Add a dedicated `web` dependency extra for browser packaging with Pygbag, PyYAML, and the canonical `pygame-ce` backend distribution.
- Add a MkDocs documentation-site configuration with explicit public navigation, GitHub Pages subpath output, and AI/MCP internal-doc exclusions.
- Add a dedicated `docs` dependency extra for static documentation builds.
- Add a framework-free static showcase shell with a Tatuy landing page and iframe-based Render Queue play page.
- Add deterministic showcase catalog discovery and validation for declared target metadata, source/docs references, and browser bundles.
- Add a tracked browser-compatibility matrix for every runnable fundamental with regression coverage that keeps the audit complete as examples change.
- Add portable window-focus events and `InputFrame.focused` so hosted runtimes can expose focus state without browser-specific game code.

#### Changed

- Unify Tatuy application loop selection around one `app.loop` setting, one loop registry, one `get_loop()`, and one `build()` path.
- Keep `TatuyApp.run()` as the desktop convenience path while moving cooperative async execution to the runtime host boundary.
- Update the browser spike tooling to package the canonical render-queue fundamental through `create_app()` and a generated web launcher instead of relying on duplicated web-specific game code.
- Add optional PyYAML configuration support without making YAML parsing part of the browser runtime.
- Remove the temporary duplicated `examples/web` browser target now that the canonical render-queue fundamental is packaged directly.
- Make the repository root explicit in pytest import paths so local development scripts resolve deterministically during test collection.
- Refresh Poetry lock metadata for the optional `config` extra and development PyYAML dependency.
- Migrate every Tatuy application target under `examples/fundamentals` to the reusable `create_app(config)` seam while preserving desktop entrypoints and example-specific default configuration.
- Split replay recording/playback from media capture throughout runtime composition, commands, input processing, frame execution, and cleanup.
- Make browser-v0 staging explicitly disable audio auto-initialization plus capture/replay write capabilities so web startup does not depend on autoplay permission or host filesystem writes.
- Package target-local `assets/` content into web staging, include asset changes in deterministic build identities, and migrate the audio fundamental to logical asset resolution.
- Select ephemeral logical storage for browser-v0 builds while preserving filesystem-backed storage as the desktop default.
- Replace the one-off web staging implementation with reusable target resolution, generated browser launchers, Pygbag invocation, normalized `build/web/play/<slug>/` output, and deterministic showcase manifest generation.
- Standardize the `pygame` and contributor extras on `pygame-ce` so desktop and browser development use one verified Pygame distribution.
- Refresh Poetry lock metadata for the `web` extra with `pygame-ce 2.5.8`, Pygbag 0.9.3, and PyYAML.
- Refresh Poetry lock metadata for the MkDocs `docs` extra and contributor environment after validating a real documentation-site build.
- Generate showcase cards and playable wrapper pages from the validated catalog manifest instead of hard-coded target data.
- Clear held keyboard/mouse state on focus loss, expose visible showcase focus state, suppress gameplay-key scrolling inside focused browser runtimes, and add async browser candidate profiles for representative input fundamentals.

### - 2026-10-24

#### Added

- Add the first Pygbag browser spike with pygame-ce, bundled pure-Python runtime dependencies, and cache-safe content-addressed staging.
- Add staging regression tests and documented manual browser workflow for custom ports, Pygbag package loading, and cache-busting URLs.

#### Changed

- Normalize collapsed polygon rasterization across upstream Pygame and pygame-ce.
- Use `pygame.image.tobytes()` for non-deprecated frame extraction while deferring deprecated test-helper snapshots for later cleanup.
- Refresh Poetry lock metadata so runtime, backend, capture, CLI, MCP, and tooling dependencies remain optional according to their extras.
- Adopt `create_app()` as the reusable construction seam for showcase targets, starting with the render-queue fundamental and getting-started guide.

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
- Add UI rendering system and activation logic, including tests for UI and visual components
- Implement DefaultSceneInitializer for scene feature provisioning and add corresponding tests
- Introduce Python-only render fallback system and refactor rendering operations
- Add guarded Git review, staging, commit, and history tools to the Tatuy MCP server
- Add an interactive MCP Apps Git review panel with per-file counts, diffs, and refresh support
- Add configurable runtime capture composition with a no-op disabled capability for browser-safe hosts
- Add an opt-in asyncio runtime host and `TatuyApp.run_async()` for cooperative/browser schedulers

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
- Refactor FX features by moving CameraFX and ScreenEffectStack to dedicated modules and adding corresponding tests
- Split runtime, backend, capture, CLI, and MCP dependencies into optional extras so the core Tatuy install no longer requires Pygame or development tooling
- Load Pillow lazily at the capture image-encoding boundary and report a targeted missing-dependency error when capture support is not installed

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

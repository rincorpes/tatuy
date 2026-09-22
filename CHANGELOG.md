# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]

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

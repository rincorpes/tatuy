# System Pipeline

Tatuy divides frame behavior into explicit phases.

```text
CONTROL
PRE_SIMULATION
PRE_SIM_COMMIT
SIMULATION
POST_SIMULATION
POST_SIM_COMMIT
PRESENTATION
```

## Control

Interpret game decisions and intent.

## Pre-simulation

Prepare state needed by the main simulation.

## Pre-simulation commit

Apply queued structural changes that should exist before simulation.

## Simulation

Run the main world state transition.

## Post-simulation

React to simulation results.

## Post-simulation commit

Apply structural work requested during simulation/post-simulation.

## Presentation

Produce the visual representation of the final frame state.

## Built-ins and game systems share the pipeline

The final scene pipeline combines:

```text
built-ins
+
scene.systems
+
scene.game_systems()
```

This means a scene's explicit game-system list is not its entire execution schedule.

For the deeper reasoning, see [System pipeline architecture](../architecture/system-pipeline.md).

---

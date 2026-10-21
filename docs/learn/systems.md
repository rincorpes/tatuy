# Systems

Systems contain behavior.

Tatuy has two primary system styles.

## BaseSystem

Runs in one phase.

```python
class GravitySystem(BaseSystem):
    phase = SystemPhase.SIMULATION
    order = 100

    def step(self, ctx):
        ...
```

Use this for a focused processor that belongs in one execution phase.

## GameSystem

A game feature may span several phases.

```python
class EnemySystem(GameSystem):
    phase_orders = {
        SystemPhase.SIMULATION: 100,
        SystemPhase.POST_SIMULATION: 300,
    }

    def on_simulation(self, ctx):
        ...

    def on_post_simulation(self, ctx):
        ...
```

Current hooks:

- `on_control`
- `on_pre_simulation`
- `on_simulation`
- `on_post_simulation`
- `on_presentation`

Only overridden hooks are scheduled.

## Ordering

Lower order values run first inside the same phase.

## `enabled(ctx)`

A system may dynamically decline to run.

## Built-in activation

Built-in registrations can also have activation predicates.

That is separate from `enabled()`.

```text
inactive
    registration says system is irrelevant

disabled
    system.enabled(ctx) says not to run
```

## Good boundaries

Prefer coherent systems:

```text
PlayerSystem
EnemySystem
WaveSystem
```

over both extremes:

```text
one class per tiny operation
```

or:

```text
EntireGameSystem
```

---

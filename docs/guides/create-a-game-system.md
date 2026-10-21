# Create a Game System

Use `GameSystem` when one gameplay concern spans one or more frame phases.

```python
class EnemySystem(GameSystem[GameContext]):
    phase_orders = {
        SystemPhase.SIMULATION: 100,
        SystemPhase.POST_SIMULATION: 300,
    }

    def on_simulation(self, ctx):
        ...

    def on_post_simulation(self, ctx):
        ...
```

Add it to the scene:

```python
def game_systems(self, ctx):
    return (
        EnemySystem(),
    )
```

Only implemented hooks are scheduled.

Use `BaseSystem` instead when the behavior is one focused processor in one phase.

---

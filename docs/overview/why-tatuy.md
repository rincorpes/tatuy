# Why Tatuy?

Tatuy explores what a small Python-first game engine can look like when gameplay stays easy to iterate on while the underlying architecture remains explicit and replaceable.

The original idea is:

> Write games in Python, then move performance-sensitive infrastructure somewhere faster when it actually becomes a problem.

Not because Python is theoretically slower.

Because a real game and a profiler demonstrate where the cost actually exists.

## Gameplay should remain readable

Game code should primarily speak in game concepts:

```text
player
enemy
wave
ball
power-up
score
```

not platform concepts:

```text
pygame surface
SDL pointer
native window handle
```

The lower-level details still exist. They simply belong at a lower layer.

## Execution should be inspectable

Tatuy aims to make questions such as these answerable:

- Which systems ran?
- Which phase did they run in?
- What was their order?
- When did structural mutations happen?
- Which collision contacts existed?
- Why did a built-in activate?
- Why was a frame slow?

Convenient behavior that becomes impossible to reason about usually becomes expensive later.

## Reusable mechanics are not game rules

The engine can understand:

- velocity integration
- collision detection
- bounds constraints
- generic entity lifetime
- rendering

It should not automatically understand:

- hitting this enemy awards 100 points
- this projectile poisons a boss
- this collision ends the wave
- this pickup grants multiball

Those are game rules.

## Composition over inheritance

Entities gain meaning through component combinations.

```text
Transform
Velocity
Circle
CircleCollider
CollisionBody
```

might describe a moving ball.

```text
Transform
Circle
Velocity
Lifetime
```

might describe a particle.

Behavior comes from systems recognizing useful state combinations.

## Structural changes are deliberate

Creating or destroying entities while systems are iterating can make execution unpredictable.

Tatuy therefore queues structural operations and commits them at known synchronization points.

```text
systems
   ↓
queued changes
   ↓
commit barrier
   ↓
world structure changes
```

## The backend boundary has a job

Today:

```text
Python game
   ↓
Tatuy
   ↓
Backend contracts
   ↓
Pygame
```

A future implementation may be:

```text
Python game
   ↓
Tatuy
   ↓
Backend contracts
   ↓
Native SDL2 backend
```

without requiring gameplay systems to change.

The boundary exists because platform infrastructure is something Tatuy genuinely may replace.

## Games drive the engine

Tatuy is developed alongside real experiments.

```text
build game
   ↓
find friction
   ↓
measure
   ↓
identify reusable problem
   ↓
improve engine
   ↓
build something harder
```

Experiments are not distractions from the engine.

They are part of the engine design process.

---

# Backends

A backend is the part of Tatuy that talks to the outside world.

It connects the engine to things such as the operating system, window management, input devices, rendering, audio, and screen capture.

Tatuy itself does **not** directly depend on Pygame, SDL, or another platform library. Instead, the engine communicates through the `Backend` protocol and a set of smaller capability protocols.

This is intentional.

The goal is to let Tatuy start simple with Python and Pygame while keeping the door open for faster native implementations later without requiring the rest of the engine — or your game — to know about it.

In other words, if everything goes according to plan:

```text
Game
  ↓
Tatuy Engine
  ↓
Backend Protocol
  ├── Window
  ├── Events
  ├── Input
  ├── Renderer
  │   ├── Shape
  │   ├── Text
  │   ├── Texture
  │   └── Clip
  ├── Audio
  └── Capture
  ↓
Concrete Backend
  └── Pygame
```

Today, the default backend is Pygame.

Tomorrow? Maybe SDL2 in C++.

Next week? Probably another refactor I swore I wasn't going to do.

---

## Why This Exists

Could Tatuy just call Pygame directly? Absolutely. That would be significantly easier... In the beginning...

But Tatuy is intended to be both a game framework and a place to experiment with how games and engines work, so the backend abstraction allows the high-level engine to remain Python-friendly while leaving performance-sensitive infrastructure replaceable.

Today:

```text
Python
  ↓
Pygame
```

Later, potentially:

```text
Python gameplay
      ↓
Tatuy
      ↓
Native C++ backend
      ↓
SDL2
```

without rewriting:

- Scenes
- ECS
- Systems
- Gameplay
- Game logic

That is the point: The backend is not there because abstracting everything is automatically good architecture.

Sometimes abstraction is just procrastination wearing glasses. It exists because **this particular boundary represents something Tatuy genuinely intends to replace**. And if one day Pong runs through a native SDL2 backend without Pong knowing or caring that the backend changed, then the abstraction did its job.

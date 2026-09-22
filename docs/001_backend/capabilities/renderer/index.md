# Renderer

The renderer is responsible for drawing a frame.

It exposes four focused capabilities:

```text
Renderer
├── Shape
├── Text
├── Texture
└── Clip
```

It also controls frame boundaries:

```python
renderer.begin_frame()

# Draw things.

renderer.end_frame()
```

In the Pygame backend:

```text
begin_frame()
```

clears the screen using the configured background color.

```text
end_frame()
```

presents the completed frame using Pygame's display flip.

The classic loop is therefore:

```python
backend.renderer.begin_frame()

# draw everything

backend.renderer.end_frame()
```

# Shapes

Shape rendering is available through:

```python
backend.renderer.shape
```

The current shape API supports:

```text
Rectangle
Line
Circle
Polygon
```

## Rectangle

```python
backend.renderer.shape.rect(
    pos=Vec2(100, 100),
    size=Size(200, 80),
    color=(255, 100, 100),
)
```

Rounded rectangles are also supported:

```python
backend.renderer.shape.rect(
    pos=Vec2(100, 100),
    size=Size(200, 80),
    color=(255, 100, 100),
    radius=12,
)
```

---

## Line

```python
backend.renderer.shape.line(
    start=Vec2(100, 100),
    end=Vec2(300, 200),
    color=(255, 255, 255),
    thickness=4,
)
```

---

## Circle

```python
backend.renderer.shape.circle(
    x=400,
    y=300,
    radius=32,
    color=(100, 200, 255),
)
```

---

## Polygon

```python
backend.renderer.shape.polygon(
    points=[
        (100, 100),
        (200, 50),
        (300, 100),
    ],
    color=(255, 255, 255),
)
```

Polygons can also be rendered as outlines:

```python
backend.renderer.shape.polygon(
    points=[
        (100, 100),
        (200, 50),
        (300, 100),
    ],
    filled=False,
)
```

RGBA colors are supported by the Pygame renderer. When alpha is required, the renderer internally uses an alpha-enabled temporary surface before compositing the result onto the window.

You should not need to care about that unless you are implementing a backend. Which means you will absolutely care about it at 2 AM one day, but not today.

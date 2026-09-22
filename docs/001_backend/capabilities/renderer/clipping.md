# Clipping

The clip capability limits rendering to a rectangular region.

A clip can be enabled using:

```python
backend.renderer.clip.set(
    pos=Vec2(100, 100),
    size=Size(300, 200),
)
```

Rendering outside that area will be clipped by the backend.

To remove the clipping region:

```python
backend.renderer.clip.clear()
```

This becomes useful for UI containers, scrollable areas, editors, and other systems where letting everything draw everywhere would turn the screen into a Jackson Pollock painting.

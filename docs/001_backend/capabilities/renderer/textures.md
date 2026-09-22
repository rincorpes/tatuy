# Textures

Textures are available through:

```python
backend.renderer.texture
```

A texture can be created from RGBA pixel data:

```python
texture = backend.renderer.texture.create(
    width,
    height,
    pixel_data,
)
```

The returned integer acts as a backend-managed texture identifier.

It can then be drawn:

```python
backend.renderer.texture.draw(
    texture,
    x=100,
    y=100,
    w=64,
    h=64,
)
```

Rotation is also supported:

```python
backend.renderer.texture.draw(
    texture,
    x=100,
    y=100,
    w=64,
    h=64,
    angle_deg=45,
)
```

Textures may also be tiled:

```python
backend.renderer.texture.tiled(
    texture,
    x=0,
    y=0,
    w=64,
    h=600,
)
```

When a texture is no longer required:

```python
backend.renderer.texture.destroy(
    texture
)
```

This API intentionally hides the concrete backend texture representation.

Pygame currently stores `pygame.Surface` objects internally. A native renderer might eventually store actual GPU texture handles.

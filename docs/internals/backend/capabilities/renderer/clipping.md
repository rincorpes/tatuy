# Renderer Clipping

`renderer.clip.set(pos: Vec2, size: Size)` maps a logical rectangle through
the renderer's viewport transform and passes the resulting integer rectangle
to `window.screen.set_clip()`.

`clear()` calls `set_clip(None)`, restoring the whole surface.
A new clip replaces the previous clip; the backend does not implement a
nested clip stack. Higher-level rendering code must restore previous state
when it needs nested clipping.

Clipping applies to direct shape drawing and blits, including translucent
shape surfaces, text, and textures. Begin-frame clearing uses surface fill
and therefore also observes an active clip. Callers should restore clipping
before expecting a full-window clear.


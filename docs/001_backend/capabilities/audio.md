# Audio

The `Audio` capability handles sound loading and playback. Audio is initialized as part of backend initialization when enabled.

A sound can be loaded using:

```python
backend.audio.load_sound(
    "explosion",
    "assets/explosion.wav",
)
```

and played using:

```python
backend.audio.play_sound(
    "explosion"
)
```

Looping is supported:

```python
backend.audio.play_sound(
    "engine",
    loops=-1,
)
```

Master volume can be changed with:

```python
backend.audio.set_master_volume(
    64
)
```

Individual sound volume can also be controlled:

```python
backend.audio.set_sound_volume(
    "explosion",
    32,
)
```

All sounds can be stopped with:

```python
backend.audio.stop_all()
```

The backend configuration uses a normalized master volume between:

```text
0.0 → silent
1.0 → full volume
```

The current Pygame audio API internally maps that value to Tatuy's existing `0–128` volume interface.

# Audio Capability

Gameplay normally uses `AudioService`, which forwards loading, playback,
master/per-sound volume, and stopping to `backend.audio`. The backend
protocol also exposes `init()` and `shutdown()`.

`PygameAudio.init()` returns when audio is disabled. Otherwise it initializes
the mixer, loads configured sounds through `FileService.validate_file_exists`,
and applies configured master volume. With `auto_init=False`, the caller
must initialize this port before loading/playing sounds.

## Volume and errors

Configuration `master_volume` uses 0.0–1.0. Initialization clamps that range,
converts it to a rounded 0–128 integer, and calls `set_master_volume`.
The runtime volume API uses integers 0–128 and clamps before converting to
Pygame's 0.0–1.0.

`load_sound(id, path)` rejects an empty ID when enabled. Reusing an ID replaces
the stored sound. `play_sound(id, loops=0)` forwards loops to Pygame and
silently ignores unknown IDs. Per-sound volume also ignores unknown IDs.

`shutdown()` quits the mixer when enabled. `stop_all()` stops mixer sound
channels; it does not unload sounds or explicitly stop the music stream.

## Current limitations

- Disabled loading/playback/init/shutdown are no-ops, but master-volume
  updates and `stop_all()` still call Pygame. On an uninitialized mixer those
  calls can fail.
- Master volume is applied to music and sounds currently loaded; it is not
  retained for sounds loaded later. Per-sound volume replaces that sound's
  volume rather than multiplying a separate master gain.
- Sound objects remain in the port's dictionary after `shutdown()`.
  Reinitialization/ownership semantics need an explicit decision.
- `pygame.init()` in the parent backend can initialize the mixer regardless
  of the port's auto-init flag.

Tests mock mixer calls; actual playback and device failure require integration
verification.


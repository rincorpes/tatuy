# Capture and Replay

Tatuy includes:

- screenshots
- input replay
- video recording

## Default hotkeys

| Key | Action |
| --- | --- |
| F2 | Screenshot |
| F3 | Start replay recording |
| F4 | Stop replay recording |
| F5 | Start replay playback |
| F6 | Stop replay playback |
| F7 | Start video recording |
| F8 | Stop and encode video |

Replay availability depends on replay settings.

## Screenshot policy

`CaptureSettings` owns root/screenshot/replay/recording directories.
`screenshot_format="png"` is the default; `"bmp"` selects real BMP output.
Video intermediate frames remain PNG. Other screenshot formats raise
`ValueError`. `hotkeys_enabled=False` disables automatic capture hotkeys;
explicit screenshot/recording commands remain available.

Legacy backend capture `enabled`, `directory`, and `format` fields are
deprecated and ignored. Move workflow configuration to `CaptureSettings`.

## Replay

Replay files store game input/timing information rather than video.

Repeatability depends on deterministic game state and consistent random seeds.

## Video

Video capture records rendered frames and encodes them through FFmpeg.

Game audio is currently separate from the recorded video stream.

---

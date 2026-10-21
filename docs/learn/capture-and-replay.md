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

## Replay

Replay files store game input/timing information rather than video.

Repeatability depends on deterministic game state and consistent random seeds.

## Video

Video capture records rendered frames and encodes them through FFmpeg.

Game audio is currently separate from the recorded video stream.

---

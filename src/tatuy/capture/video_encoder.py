from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from tatuy.capture.settings import CaptureSettings


@dataclass(frozen=True)
class VideoFrame:
    path: Path
    timestamp: float


@dataclass(frozen=True)
class EncodeResult:
    ok: bool
    output_path: Path
    error: str | None = None


class VideoEncoder:
    def encode(
        self,
        *,
        base_dir: Path,
        frames: tuple[VideoFrame, ...],
        duration: float,
        settings: CaptureSettings,
    ) -> EncodeResult:
        output = base_dir / "video.mp4"

        if not frames:
            return EncodeResult(
                ok=False,
                output_path=output,
                error="No video frames were saved",
            )

        concat_path = base_dir / "frames.ffconcat"
        duration = max(duration, frames[-1].timestamp + 0.001)

        try:
            lines = ["ffconcat version 1.0"]

            for index, frame in enumerate(frames):
                end = (
                    frames[index + 1].timestamp
                    if index + 1 < len(frames)
                    else duration
                )

                # Extend the first image back to recording time zero.
                start = 0.0 if index == 0 else frame.timestamp
                hold = max(0.001, end - start)

                # Generated frame names are ASCII and contain no quotes.
                relative = frame.path.relative_to(base_dir).as_posix()

                lines.extend(
                    [
                        f"file '{relative}'",
                        "option framerate 1000",
                        f"duration {hold:.9f}",
                    ]
                )

            # Repeat the final image so its hold duration is represented.
            final_path = frames[-1].path.relative_to(base_dir).as_posix()

            lines.extend(
                [
                    f"file '{final_path}'",
                    "option framerate 1000",
                ]
            )

            concat_path.write_text(
                "\n".join(lines) + "\n",
                encoding="utf-8",
            )

            filters = (
                "pad=ceil(iw/2)*2:ceil(ih/2)*2," f"fps={settings.video_fps}"
            )

            command = [
                settings.ffmpeg_path,
                "-nostdin",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_path),
                "-vf",
                filters,
                "-t",
                f"{duration:.9f}",
                "-an",
                "-c:v",
                settings.video_codec,
                "-crf",
                str(settings.video_crf),
                "-preset",
                settings.video_preset,
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(output),
            ]

            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                errors="replace",
                check=False,
            )

            if process.returncode != 0:
                return EncodeResult(
                    ok=False,
                    output_path=output,
                    error=process.stderr.strip() or "FFmpeg failed",
                )

            return EncodeResult(
                ok=True,
                output_path=output,
            )

        except Exception as exc:
            return EncodeResult(
                ok=False,
                output_path=output,
                error=str(exc),
            )

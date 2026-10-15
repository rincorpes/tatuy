from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from tatuy.tooling.profiler.snapshot import ProfileSnapshot


def export_profile(
    snapshot: ProfileSnapshot,
    path: str | Path,
) -> Path:
    output = Path(path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            asdict(snapshot),
            file,
            indent=2,
            default=str,
        )

    return output

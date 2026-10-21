from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateTargetInput:
    kind: str
    name: str
    description: str = ""
    tags: tuple[str, ...] = ()
    path: str | None = None
    tatuy_source: str | None = None
    tatuy_version: str | None = None

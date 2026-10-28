from __future__ import annotations

from dataclasses import dataclass

from tatuy_cli.scaffolding.model import TargetKind, TatuySource


@dataclass(frozen=True)
class CreateTargetInput:
    kind: TargetKind
    name: str
    description: str = ""
    tags: tuple[str, ...] = ()
    path: str | None = None
    tatuy_source: TatuySource | None = None
    tatuy_version: str | None = None
    showcase: bool = False

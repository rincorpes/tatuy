from __future__ import annotations

from dataclasses import dataclass, field

from tatuy.engine.render.pipeline import RenderPipeline
from tatuy.engine.system import SystemPipeline


@dataclass
class EnginePipelines:
    system: SystemPipeline = field(default_factory=SystemPipeline)
    render: RenderPipeline = field(default_factory=RenderPipeline)

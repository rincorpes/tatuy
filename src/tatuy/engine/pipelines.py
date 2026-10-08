from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from tatuy.ecs.world import TWorld
from tatuy.engine.builtins import BuiltinSystemCatalog
from tatuy.engine.render.pipeline import RenderPipeline
from tatuy.engine.system import (
    SceneStructuralCommitter,
    SystemPipeline,
    SystemRegistration,
)
from tatuy.features.lifecycle.commit import LifecycleCommitter
from tatuy.scenes.context import SceneContext, TContext, TIntent

if TYPE_CHECKING:
    from tatuy.scenes.scene import Scene


@dataclass
class SystemPipelineFactory:
    builtins: BuiltinSystemCatalog = field(
        default_factory=BuiltinSystemCatalog
    )

    def create(
        self, scene: Scene[TWorld, TIntent, TContext], ctx: SceneContext
    ) -> SystemPipeline[TContext]:
        # The catalog creates fresh system instances.
        entries = dict(self.builtins.create(scene, ctx))

        for key, override in scene.builtin_overrides(ctx).items():
            if key not in entries:
                raise KeyError(f"Unknown built-in system: {key}")

            if override is None:
                del entries[key]
            else:
                entries[key] = override

        registrations = [
            entry for entry in entries.values() if entry is not None
        ]

        registrations.extend(
            SystemRegistration(system) for system in scene.systems
        )

        registrations.extend(
            SystemRegistration(system) for system in scene.game_systems(ctx)
        )

        committer = SceneStructuralCommitter[TContext](
            components=scene.structural_commands,
            lifecycle=LifecycleCommitter[TContext](scene.factory),
        )

        return SystemPipeline(
            committer=committer,
            registrations=registrations,
        )


@dataclass
class EnginePipelines:
    system: SystemPipelineFactory = field(
        default_factory=SystemPipelineFactory
    )
    render: RenderPipeline = field(default_factory=RenderPipeline)

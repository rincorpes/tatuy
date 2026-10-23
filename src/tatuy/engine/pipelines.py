"""Generic engine and scene pipeline construction contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Generic, Mapping, Protocol

from tatuy.ecs.world import TWorld
from tatuy.engine.render.pipeline import RenderPipeline
from tatuy.engine.system import (
    StructuralCommitter,
    SystemPipeline,
    SystemRegistration,
)
from tatuy.scenes.context import SceneContext, TContext, TIntent

if TYPE_CHECKING:
    from tatuy.scenes.scene import Scene


class SystemCatalog(Protocol, Generic[TContext]):
    """Provide named system registrations for a scene."""

    def create(
        self,
        scene: Scene,
        ctx: SceneContext,
    ) -> Mapping[str, SystemRegistration[TContext]]:
        """Create fresh named registrations for one scene."""


@dataclass
class SystemPipelineFactory(Generic[TContext]):
    """Build scene pipelines from injected registrations and committers."""

    catalog: SystemCatalog[TContext]
    committer_factory: Callable[
        [Scene, SceneContext], StructuralCommitter[TContext]
    ]

    def create(
        self,
        scene: Scene[TWorld, TIntent, TContext],
        ctx: SceneContext,
    ) -> SystemPipeline[TContext]:
        """Build one scene pipeline from injected composition dependencies."""
        entries = dict(self.catalog.create(scene, ctx))

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

        return SystemPipeline(
            committer=self.committer_factory(scene, ctx),
            registrations=registrations,
        )


@dataclass
class EnginePipelines:
    """Engine-owned pipelines that do not belong to scene composition."""

    render: RenderPipeline = field(default_factory=RenderPipeline)

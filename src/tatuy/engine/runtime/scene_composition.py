"""Default runtime-owned scene feature composition."""

from __future__ import annotations

from tatuy.ecs.structural import StructuralCommandBuffer
from tatuy.features.bounds.resources import BoundsFrame, WorldBounds
from tatuy.features.fx.camera import CameraFX
from tatuy.features.fx.screen import ScreenEffectStack
from tatuy.features.lifecycle.resources import LifecycleQueue, SpawnRegistry
from tatuy.scenes.context import SceneContext
from tatuy.scenes.scene import Scene


class DefaultSceneInitializer:
    """Provision Tatuy's default optional feature resources for a scene."""

    def initialize(self, scene: Scene, ctx: SceneContext) -> None:
        """Install default feature services/resources and process declarations."""
        world = scene.world

        for resource_type in scene.shared_resource_types:
            world.add_resource(ctx.resources.get(resource_type))

        for resource in scene.resources(ctx):
            world.add_resource(resource)

        scene.structural_commands = StructuralCommandBuffer()
        world.add_resource(scene.structural_commands)

        scene.screen_fx = ScreenEffectStack()
        scene.camera_fx = CameraFX()

        if not world.has_resource(LifecycleQueue):
            world.add_resource(LifecycleQueue())

        if not world.has_resource(SpawnRegistry):
            world.add_resource(SpawnRegistry())

        registry = world.get_resource(SpawnRegistry)
        queue = world.get_resource(LifecycleQueue)

        definitions = dict(scene.spawn_definitions(ctx))
        duplicates = registry.definitions.keys() & definitions.keys()
        if duplicates:
            raise ValueError(
                f"Duplicate spawn definitions: {sorted(duplicates)}"
            )

        registry.definitions.update(definitions)

        placements = tuple(scene.entities(ctx))
        for placement in placements:
            if placement.definition not in registry.definitions:
                raise ValueError(
                    f"Unknown spawn definition: {placement.definition}"
                )

        for placement in placements:
            queue.request_spawn(
                placement.definition,
                delay=placement.delay,
                kwargs=placement.kwargs,
            )

        bounds = scene.bounds(ctx)
        if bounds is not None:
            world.add_resource(WorldBounds(bounds))
            world.add_resource(BoundsFrame())

        bounds_border = scene.bounds_border(ctx)
        if bounds_border is not None:
            world.add_resource(bounds_border)

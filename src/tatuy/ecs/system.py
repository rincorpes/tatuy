from __future__ import annotations

from enum import IntEnum
from itertools import combinations
from typing import Generic

from tatuy.ecs.component import (
    BoundsBehavior,
    BoundsConstraint,
    BoxCollider,
    Circle,
    CircleCollider,
    CollisionBody,
    DespawnReason,
    Lifetime,
    Movement,
    MovementControls,
    Paddle,
    PaddleMotionSample,
    Rect,
    Respawn,
    SpawnOrigin,
    Text,
    Transform,
    Velocity,
)
from tatuy.ecs.entity_factory import EntityFactory
from tatuy.ecs.resources import (
    BoundsBounceEvent,
    BoundsFrame,
    CollisionContact,
    CollisionFrame,
    LifecycleQueue,
    SpawnRegistry,
    WorldBounds,
    WorldBoundsBorder,
)
from tatuy.ecs.world import TWorld
from tatuy.geometry.bounds import (
    BoundsBounce,
    BoundsClamp,
    BoundsQuery,
    BoundsSide,
    BoundsWrap,
)
from tatuy.geometry.collision import CollisionGeometry
from tatuy.graphics.bounds_border import BoundsBorderRenderer
from tatuy.math.vec2 import Vec2
from tatuy.physics.colliders import ColliderAccess
from tatuy.physics.response import CollisionVelocityRule
from tatuy.scenes.context import BaseTickContext, TContext, TIntent
from tatuy.ui.intent import UiIntent
from tatuy.ui.interaction import UiPointerController
from tatuy.ui.layout import UiLayoutResolver
from tatuy.ui.render import UiRenderer


class SystemPhase(IntEnum):
    """
    High-level execution buckets for scene systems.

    Keep values spaced to leave room for future insertions without churn.
    """

    CONTROL = 10
    SIMULATION = 20
    PRESENTATION = 30


class BaseSystem(Generic[TContext]):

    phase: SystemPhase = SystemPhase.SIMULATION
    order: int = 0

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def enabled(
        self, ctx: TContext  # pylint: disable=unused-argument
    ) -> bool:
        return True

    def step(self, ctx: TContext):
        raise NotImplementedError


class VelocityIntegrationSystem(BaseSystem[TContext]):
    phase = SystemPhase.SIMULATION

    def step(self, ctx: BaseTickContext[TWorld, TIntent]) -> None:
        for _, transform, velocity in ctx.world.query(
            Transform,
            Velocity,
        ):
            transform.position.x += velocity.value.x * ctx.dt
            transform.position.y += velocity.value.y * ctx.dt


class RenderSystem(BaseSystem[TContext]):
    phase = SystemPhase.PRESENTATION

    def __init__(self) -> None:
        self._ui_renderer = UiRenderer()

    def step(self, ctx: BaseTickContext[TWorld, TIntent]):
        for _, transform, rect in ctx.world.query(Transform, Rect):
            if not rect.visible:
                continue
            z = rect.z
            ctx.render_queue.rect(
                center=transform.position,
                size=rect.size,
                color=rect.color,
                layer=rect.layer,
                z=z,
            )
        for _, transform, text in ctx.world.query(Transform, Text):
            if not text.visible:
                continue

            ctx.render_queue.text(
                x=transform.position.x,
                y=transform.position.y,
                text=text.content,
                color=text.color,
                font_size=text.font_size,
                align=text.align,
                valign=text.valign,
                layer=text.layer,
                z=text.z,
            )
        for _, transform, circle in ctx.world.query(Transform, Circle):
            if not circle.visible:
                continue

            ctx.render_queue.circle(
                center=transform.position,
                radius=circle.radius,
                color=circle.color,
                layer=circle.layer,
                z=circle.z,
            )

        self._ui_renderer.submit(ctx.world, ctx.render_queue)


class MovementControlSystem(BaseSystem[TContext]):
    def step(self, ctx: BaseTickContext[TWorld, TIntent]):
        for _, movement, controls, velocity in ctx.world.query(
            Movement,
            MovementControls,
            Velocity,
        ):
            direction = Vec2.zero()

            if controls.up and ctx.intent.move_up:
                direction.y -= 1

            if controls.down and ctx.intent.move_down:
                direction.y += 1

            if controls.left and ctx.intent.move_left:
                direction.x -= 1

            if controls.right and ctx.intent.move_right:
                direction.x += 1

            if controls.normalize and direction.length_squared() > 0:
                direction = direction.normalized()

            velocity.value = direction * movement.speed


class BoundsConstraintSystem(BaseSystem[TContext]):
    def __init__(self) -> None:
        self._colliders = ColliderAccess()
        self._query = BoundsQuery()
        self._clamp = BoundsClamp()
        self._bounce = BoundsBounce()
        self._wrap = BoundsWrap()

    def step(
        self,
        ctx: BaseTickContext[TWorld, TIntent],
    ) -> None:
        bounds = ctx.world.get_resource(WorldBounds).bounds

        bounds_frame = ctx.world.get_resource(BoundsFrame)
        bounds_frame.bounces.clear()

        for entity, constraint, transform in ctx.world.query(
            BoundsConstraint,
            Transform,
        ):
            if constraint.behavior == BoundsBehavior.NONE:
                continue

            shape = self._colliders.geometry(
                ctx.world,
                entity,
            )

            match constraint.behavior:
                case BoundsBehavior.CLAMP:
                    transform.position = self._clamp.apply(
                        bounds,
                        transform.position,
                        shape,
                        sides=constraint.sides,
                    )

                case BoundsBehavior.BOUNCE:
                    velocity = ctx.world.get_component(
                        entity,
                        Velocity,
                    )

                    result = self._bounce.apply(
                        bounds,
                        transform.position,
                        shape,
                        velocity.value,
                        sides=constraint.sides,
                    )

                    transform.position = result.position
                    velocity.value = result.velocity

                    if result.bounced_sides != BoundsSide.NONE:
                        bounds_frame.bounces.append(
                            BoundsBounceEvent(
                                entity=entity,
                                sides=result.bounced_sides,
                            )
                        )

                case BoundsBehavior.WRAP:
                    result = self._wrap.apply(
                        bounds,
                        transform.position,
                        shape,
                        sides=constraint.sides,
                    )

                    transform.position = result.position

                case BoundsBehavior.DESPAWN:
                    outside = self._query.outside_sides(
                        bounds,
                        shape,
                        sides=constraint.sides,
                    )

                    if outside != BoundsSide.NONE:
                        queue = ctx.world.get_resource(LifecycleQueue)

                        queue.request_despawn(
                            entity,
                            DespawnReason.OUT_OF_BOUNDS,
                        )


class SpawnSystem(BaseSystem[TContext]):
    def __init__(self, factory: EntityFactory) -> None:
        self._factory = factory

    def step(
        self,
        ctx: BaseTickContext[TWorld, TIntent],
    ) -> None:
        queue = ctx.world.get_resource(LifecycleQueue)
        registry = ctx.world.get_resource(SpawnRegistry)

        # Process this batch. Any newly queued requests wait
        # until the next update.
        requests = queue.spawns
        queue.spawns = []

        for request in requests:
            request.remaining -= ctx.dt

            if request.remaining > 0:
                queue.spawns.append(request)
                continue

            definition = registry.definitions.get(request.definition)

            if definition is None:
                raise ValueError(
                    f"Unknown spawn definition: {request.definition}"
                )

            entity = self._factory.create(
                definition.blueprint,
                **definition.make_kwargs(),
            )

            ctx.world.add_component(
                entity,
                SpawnOrigin(definition=request.definition),
            )

            if definition.respawn is not None:
                # Respawn is frozen and contains immutable values,
                # so sharing this policy is safe.
                ctx.world.add_component(
                    entity,
                    definition.respawn,
                )

            if definition.lifetime is not None:
                # Each entity needs its own mutable countdown.
                ctx.world.add_component(
                    entity,
                    Lifetime(remaining=definition.lifetime),
                )


class LifetimeSystem(BaseSystem[TContext]):
    def step(
        self,
        ctx: BaseTickContext[TWorld, TIntent],
    ) -> None:
        queue = ctx.world.get_resource(LifecycleQueue)

        for entity, lifetime in ctx.world.query(Lifetime):
            lifetime.remaining -= ctx.dt

            if lifetime.remaining <= 0:
                queue.request_despawn(
                    entity,
                    DespawnReason.LIFETIME_EXPIRED,
                )


class DespawnSystem(BaseSystem[TContext]):
    def step(
        self,
        ctx: BaseTickContext[TWorld, TIntent],
    ) -> None:
        queue = ctx.world.get_resource(LifecycleQueue)

        requests = queue.despawns
        queue.despawns = {}

        for request in requests.values():
            entity = request.entity

            # Another removal may already have deleted this entity.
            if entity not in ctx.world.entities:
                continue

            can_respawn = (
                request.allow_respawn
                and ctx.world.has_component(entity, SpawnOrigin)
                and ctx.world.has_component(entity, Respawn)
            )

            if can_respawn:
                origin = ctx.world.get_component(
                    entity,
                    SpawnOrigin,
                )
                policy = ctx.world.get_component(
                    entity,
                    Respawn,
                )

                if request.reason in policy.reasons:
                    queue.request_spawn(
                        origin.definition,
                        delay=policy.delay,
                    )

            ctx.world.destroy_entity(entity)


class CollisionDetectionSystem(BaseSystem[TContext]):
    phase = SystemPhase.SIMULATION

    def __init__(self) -> None:
        self._colliders = ColliderAccess()
        self._geometry = CollisionGeometry()

    def step(
        self,
        ctx: BaseTickContext[TWorld, TIntent],
    ) -> None:
        frame = ctx.world.get_resource(CollisionFrame)
        frame.contacts.clear()

        colliders = []

        for entity, transform in ctx.world.query(Transform):
            collider = self._colliders.find(
                ctx.world,
                entity,
            )

            if collider is None:
                continue

            if not isinstance(
                collider,
                (BoxCollider, CircleCollider),
            ):
                raise NotImplementedError(
                    "Entity collisions currently support " "boxes and circles"
                )

            shape = self._colliders.shape(
                transform.position,
                collider,
            )

            colliders.append((entity, shape))

        colliders.sort(key=lambda row: row[0])

        for first, second in combinations(colliders, 2):
            entity_a, shape_a = first
            entity_b, shape_b = second

            result = self._geometry.find(
                shape_a,
                shape_b,
            )

            if result is None:
                continue

            normal, penetration = result

            frame.contacts.append(
                CollisionContact(
                    entity_a=entity_a,
                    entity_b=entity_b,
                    normal=normal,
                    penetration=penetration,
                )
            )


class CollisionResponseSystem(BaseSystem[TContext]):
    def __init__(
        self,
        velocity_rules: tuple[CollisionVelocityRule, ...] = (),
    ) -> None:
        self._velocity_rules = velocity_rules
        self._colliders = ColliderAccess()

    def step(
        self,
        ctx: BaseTickContext[TWorld, TIntent],
    ) -> None:
        world = ctx.world
        frame = world.get_resource(CollisionFrame)

        for contact in frame.contacts:
            entity_a = contact.entity_a
            entity_b = contact.entity_b

            # Detection also supports entities without physical bodies.
            required = (
                Transform,
                CollisionBody,
                Velocity,
            )
            if not all(
                world.has_component(entity, component)
                for entity in (entity_a, entity_b)
                for component in required
            ):
                continue

            collider_a = self._colliders.get(world, entity_a)
            collider_b = self._colliders.get(world, entity_b)

            if collider_a.is_sensor or collider_b.is_sensor:
                continue

            transform_a = world.get_component(entity_a, Transform)
            transform_b = world.get_component(entity_b, Transform)

            body_a = world.get_component(entity_a, CollisionBody)
            body_b = world.get_component(entity_b, CollisionBody)

            velocity_a = world.get_component(entity_a, Velocity).value
            velocity_b = world.get_component(entity_b, Velocity).value

            inverse_mass_a = body_a.inverse_mass
            inverse_mass_b = body_b.inverse_mass
            total_inverse_mass = inverse_mass_a + inverse_mass_b

            # Two immovable bodies cannot be separated by this solver.
            if total_inverse_mass == 0:
                continue

            normal = contact.normal

            # First remove the overlap. Lighter bodies move farther.
            correction = contact.penetration / total_inverse_mass

            transform_a.position.x -= normal.x * correction * inverse_mass_a
            transform_a.position.y -= normal.y * correction * inverse_mass_a

            transform_b.position.x += normal.x * correction * inverse_mass_b
            transform_b.position.y += normal.y * correction * inverse_mass_b

            # Relative velocity along the contact normal.
            relative_x = velocity_b.x - velocity_a.x
            relative_y = velocity_b.y - velocity_a.y
            normal_speed = relative_x * normal.x + relative_y * normal.y

            # Correct penetration, but do not bounce bodies that
            # are already moving apart.
            if normal_speed >= 0:
                continue

            replacement = None

            for rule in self._velocity_rules:
                replacement = rule.resolve(world, contact)

                if replacement is not None:
                    break

            if replacement is not None:
                world.get_component(entity_a, Velocity).value = replacement.a

                world.get_component(entity_b, Velocity).value = replacement.b

                continue

            restitution = min(
                body_a.restitution,
                body_b.restitution,
            )

            impulse = -(1.0 + restitution) * normal_speed / total_inverse_mass

            velocity_a.x -= normal.x * impulse * inverse_mass_a
            velocity_a.y -= normal.y * impulse * inverse_mass_a

            velocity_b.x += normal.x * impulse * inverse_mass_b
            velocity_b.y += normal.y * impulse * inverse_mass_b


class UiLayoutSystem(BaseSystem[TContext]):
    phase = SystemPhase.CONTROL

    def step(self, ctx: BaseTickContext[TWorld, TIntent]):
        UiLayoutResolver(ctx.world, ctx.scene_context.viewport).layout()


class UiPointerSystem(BaseSystem[TContext]):
    phase = SystemPhase.CONTROL

    def __init__(self) -> None:
        self._controller = UiPointerController()

    def step(self, ctx: BaseTickContext[TWorld, TIntent]):
        if not isinstance(ctx.intent, UiIntent):
            raise TypeError(
                "UiPointerSystem requires an intent derived from UiIntent"
            )

        self._controller.update(
            ctx.world,
            ctx.intent,
            ctx.scene_context.commands,
        )


class WorldBoundsRenderSystem(BaseSystem[TContext]):
    phase = SystemPhase.PRESENTATION

    def __init__(self) -> None:
        self._renderer = BoundsBorderRenderer()

    def step(
        self,
        ctx: BaseTickContext[TWorld, TIntent],
    ) -> None:
        bounds = ctx.world.get_resource(WorldBounds)
        border = ctx.world.get_resource(WorldBoundsBorder)

        self._renderer.submit(
            bounds.bounds,
            border,
            ctx.render_queue,
        )


class PaddleMotionCaptureSystem(BaseSystem[TContext]):
    phase = SystemPhase.SIMULATION

    def step(self, ctx: BaseTickContext[TWorld, TIntent]):
        for _, _, transform, sample in ctx.world.query(
            Paddle,
            Transform,
            PaddleMotionSample,
        ):
            sample.start_position = Vec2(
                transform.position.x,
                transform.position.y,
            )


class PaddleMotionMeasureSystem(BaseSystem[TContext]):
    phase = SystemPhase.SIMULATION

    def step(self, ctx: BaseTickContext[TWorld, TIntent]):
        for _, _, transform, velocity, sample in ctx.world.query(
            Paddle,
            Transform,
            Velocity,
            PaddleMotionSample,
        ):
            if sample.start_position is None or ctx.dt <= 0:
                velocity.value = Vec2.zero()
                continue

            velocity.value = (
                transform.position - sample.start_position
            ) / ctx.dt

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from random import Random

from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs import (
    BaseSystem,
    EntityFactory,
    EntityId,
    SystemPhase,
    TypedEntityBlueprint,
    World,
)
from tatuy.features.bounds import (
    WorldBounds,
    WorldBoundsBorder,
    WorldBoundsRenderSystem,
)
from tatuy.features.lifecycle import (
    DespawnReason,
    LifecycleQueue,
    Respawn,
    SpawnDefinition,
    SpawnRegistry,
)
from tatuy.features.lifecycle.systems import DespawnSystem, SpawnSystem
from tatuy.features.movement import (
    DesiredMovement,
    MovementControls,
    MovementControlSystem,
)
from tatuy.features.spatial import Transform
from tatuy.features.visual import (
    RectBlueprint,
    RectBlueprintAttrs,
    RectBlueprintBase,
    RenderSystem,
)
from tatuy.geometry.bounds import Bounds
from tatuy.geometry.grid import GridLayout, GridPlacement, GridSpec
from tatuy.geometry.size import Size
from tatuy.input.keys import Key
from tatuy.math.vec2 import Vec2
from tatuy.scenes import Intent, Scene, SceneRegistry, SceneTickContext


class SnakeWorld(World): ...


class SnakeIntent(Intent):
    def update_from(self, input_frame):
        self.move_left = input_frame.is_pressed(Key.A)
        self.move_up = input_frame.is_pressed(Key.W)
        self.move_right = input_frame.is_pressed(Key.D)
        self.move_down = input_frame.is_pressed(Key.S)


class SnakeSceneTickContext(SceneTickContext[SnakeWorld, SnakeIntent]): ...


@dataclass
class SnakeRandom:
    value: Random


@dataclass(frozen=True)
class GridPosition:
    column: int
    row: int


@dataclass
class SnakeBoard:
    bounds: Bounds
    rows: int
    columns: int
    cell_size: int
    cells: dict[tuple[int, int], GridPlacement]

    def contains(self, position: GridPosition) -> bool:
        return (
            0 <= position.column < self.columns
            and 0 <= position.row < self.rows
        )

    def placement(self, position: GridPosition) -> GridPlacement:
        return self.cells[(position.row, position.column)]


class SnakeDirection(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def column_delta(self) -> int:
        return self.value[0]

    @property
    def row_delta(self) -> int:
        return self.value[1]


@dataclass
class SnakeSegment: ...


@dataclass
class Snake:
    segments: list[EntityId]
    direction: SnakeDirection
    queued_direction: SnakeDirection
    step_interval: float = 0.15
    accumulator: float = 0.0


OPPOSITE_DIRECTION = {
    SnakeDirection.UP: SnakeDirection.DOWN,
    SnakeDirection.DOWN: SnakeDirection.UP,
    SnakeDirection.LEFT: SnakeDirection.RIGHT,
    SnakeDirection.RIGHT: SnakeDirection.LEFT,
}


class SnakeEntityFactory(EntityFactory): ...


@dataclass(frozen=True, kw_only=True)
class SegmentAttrs(RectBlueprintAttrs):
    grid_position: GridPosition


@SnakeEntityFactory.blueprint("segment")
class SnakeSegmentBlueprint(RectBlueprintBase[SnakeWorld, SegmentAttrs]):

    identity = SnakeSegment
    attrs_type = SegmentAttrs

    def compose(self, attrs):
        return (attrs.grid_position,)


@dataclass
class Food: ...


@dataclass(frozen=True, kw_only=True)
class FoodAttrs(RectBlueprintAttrs):
    grid_position: GridPosition


@SnakeEntityFactory.blueprint("food")
class FoodBlueprint(RectBlueprint[SnakeWorld]):

    identity = Food
    attrs_type = FoodAttrs

    def compose(self, attrs: FoodAttrs):
        return (attrs.grid_position,)


@dataclass(frozen=True, kw_only=True)
class SnakeAttrs(RectBlueprintAttrs):
    segments: list[EntityId]


@SnakeEntityFactory.blueprint("snake")
class SnakeBlueprint(TypedEntityBlueprint[SnakeWorld, SnakeAttrs]):

    attrs_type = SnakeAttrs

    def build_attrs(self, world, entity, attrs):
        world.add_component(
            entity,
            Snake(
                segments=attrs.segments,
                direction=SnakeDirection.RIGHT,
                queued_direction=SnakeDirection.RIGHT,
            ),
        )

    def compose(self, attrs):
        return (MovementControls(), DesiredMovement())


class GridDebugRenderSystem(BaseSystem[SnakeSceneTickContext]):
    phase = SystemPhase.PRESENTATION

    def __init__(
        self,
        color=(45, 50, 65),
        thickness=1,
    ):
        self.color = color
        self.thickness = thickness

    def step(self, ctx):
        board = ctx.world.get_resource(SnakeBoard)
        bounds = board.bounds

        # Internal vertical lines.
        for column in range(1, board.columns):
            x = bounds.left + column * board.cell_size

            ctx.render_queue.line(
                a=Vec2(x, bounds.top),
                b=Vec2(x, bounds.bottom),
                color=self.color,
                thickness=self.thickness,
                layer="debug",
            )

        # Internal horizontal lines.
        for row in range(1, board.rows):
            y = bounds.top + row * board.cell_size

            ctx.render_queue.line(
                a=Vec2(bounds.left, y),
                b=Vec2(bounds.right, y),
                color=self.color,
                thickness=self.thickness,
                layer="debug",
            )


class SnakeDirectionSystem(BaseSystem[SnakeSceneTickContext]):
    phase = SystemPhase.CONTROL

    def step(self, ctx):
        for _, snake, desired in ctx.world.query(
            Snake,
            DesiredMovement,
        ):
            direction = desired.direction

            if direction.length_squared() == 0:
                continue

            if abs(direction.x) >= abs(direction.y):
                requested = (
                    SnakeDirection.RIGHT
                    if direction.x > 0
                    else SnakeDirection.LEFT
                )
            else:
                requested = (
                    SnakeDirection.DOWN
                    if direction.y > 0
                    else SnakeDirection.UP
                )

            if requested == OPPOSITE_DIRECTION[snake.direction]:
                continue

            snake.queued_direction = requested
            # snake.started = True


def segment_kwargs(
    board: SnakeBoard,
    grid_position: GridPosition,
) -> dict:
    placement = board.placement(grid_position)

    return {
        "grid_position": grid_position,
        "position": Vec2(
            placement.center.x,
            placement.center.y,
        ),
        "size": Size(
            board.cell_size - 6,
            board.cell_size - 6,
        ),
        "color": (80, 220, 140),
    }


class SnakeMovementSystem(BaseSystem[SnakeSceneTickContext]):
    phase = SystemPhase.SIMULATION

    def __init__(self, factory: EntityFactory):
        self._factory = factory

    def step(self, ctx):
        for _, snake in ctx.world.query(Snake):
            snake.accumulator += ctx.dt

            while snake.accumulator >= snake.step_interval:
                snake.accumulator -= snake.step_interval
                self._advance(ctx, snake)

    def _advance(
        self,
        ctx: SnakeSceneTickContext,
        snake: Snake,
    ) -> None:
        world = ctx.world
        board = world.get_resource(SnakeBoard)

        snake.direction = snake.queued_direction

        positions = [
            world.get_component(entity, GridPosition)
            for entity in snake.segments
        ]

        if not positions:
            return

        old_head = positions[0]
        old_tail = positions[-1]

        new_head = GridPosition(
            column=old_head.column + snake.direction.column_delta,
            row=old_head.row + snake.direction.row_delta,
        )

        if not board.contains(new_head):
            return  # Later: game over.

        food_data = next(
            world.query(Food, GridPosition),
            None,
        )

        food_entity = (
            food_data[0]
            if food_data is not None and food_data[2] == new_head
            else None
        )
        ate_food = food_entity is not None

        occupied_body = set(positions[1:] if ate_food else positions[1:-1])

        if new_head in occupied_body:
            return  # Later: game over.
        new_positions = [
            new_head,
            *positions[:-1],
        ]

        for entity, position in zip(
            snake.segments,
            new_positions,
        ):
            world.add_component(entity, position)

        if food_entity is not None:
            new_segment = self._factory.create(
                "segment",
                **segment_kwargs(board, old_tail),
            )

            snake.segments.append(new_segment)

            lifecycle = world.get_resource(LifecycleQueue)

            lifecycle.request_despawn(
                food_entity,
                DespawnReason.SCRIPTED,
            )


class GridTransformSystem(BaseSystem[SnakeSceneTickContext]):
    phase = SystemPhase.SIMULATION

    def step(self, ctx):
        board = ctx.world.get_resource(SnakeBoard)

        for _, grid_position, transform in ctx.world.query(
            GridPosition,
            Transform,
        ):
            placement = board.placement(grid_position)

            transform.position = Vec2(
                placement.center.x,
                placement.center.y,
            )


@SceneRegistry.implementation("main")
class SnakeScene(Scene[SnakeWorld, SnakeIntent, SnakeSceneTickContext]):

    world_type = SnakeWorld
    intent_type = SnakeIntent
    tick_context_type = SnakeSceneTickContext
    factory_type = SnakeEntityFactory

    def on_enter(self, ctx):
        w, h = ctx.viewport.window_w, ctx.viewport.window_h

        available_area = Bounds(left=125, top=25, right=w - 125, bottom=h - 25)

        cell_size = 24

        columns = int(available_area.width // cell_size)
        rows = int(available_area.height // cell_size)

        grid_width = columns * cell_size
        grid_height = rows * cell_size

        grid_left = (
            available_area.left + (available_area.width - grid_width) / 2
        )

        grid_top = (
            available_area.top + (available_area.height - grid_height) / 2
        )

        grid_bounds = Bounds(
            left=grid_left,
            top=grid_top,
            right=grid_left + grid_width,
            bottom=grid_top + grid_height,
        )

        self.world.add_resource(WorldBounds(grid_bounds))
        self.world.add_resource(
            WorldBoundsBorder(thickness=1, color=(90, 100, 125))
        )
        placements = GridLayout().resolve(
            grid_bounds,
            GridSpec(
                rows=rows,
                columns=columns,
                cell_width=cell_size,
                cell_height=cell_size,
            ),
        )
        board = SnakeBoard(
            bounds=grid_bounds,
            rows=rows,
            columns=columns,
            cell_size=cell_size,
            cells={
                (placement.row, placement.column): placement
                for placement in placements
            },
        )

        self.world.add_resource(board)

        self.world.add_resource(SnakeRandom(Random(12345)))

        def make_food_kwargs() -> dict:
            board = self.world.get_resource(SnakeBoard)
            rng = self.world.get_resource(SnakeRandom).value

            occupied = {
                position
                for _, _, position in self.world.query(
                    SnakeSegment,
                    GridPosition,
                )
            }

            available = [
                GridPosition(column=column, row=row)
                for row in range(board.rows)
                for column in range(board.columns)
                if GridPosition(column=column, row=row) not in occupied
            ]

            if not available:
                raise RuntimeError("Cannot spawn food: the board is full")

            grid_position = rng.choice(available)
            placement = board.placement(grid_position)

            return {
                "grid_position": grid_position,
                "position": Vec2(x=placement.center.x, y=placement.center.y),
                "size": Size(
                    width=board.cell_size - 6, height=board.cell_size - 6
                ),
                "color": (255, 92, 114),
            }

        self.world.add_resource(
            SpawnRegistry(
                definitions={
                    "food": SpawnDefinition(
                        blueprint="food",
                        make_kwargs=make_food_kwargs,
                        respawn=Respawn(
                            delay=0.0,
                            reasons=frozenset(
                                {
                                    DespawnReason.SCRIPTED,
                                }
                            ),
                        ),
                    ),
                }
            )
        )

        queue = self.world.add_resource(LifecycleQueue())

        self.systems = (
            DespawnSystem(),
            SpawnSystem(self.factory),
            MovementControlSystem(),
            SnakeDirectionSystem(),
            SnakeMovementSystem(self.factory),
            GridTransformSystem(),
            WorldBoundsRenderSystem(),
            GridDebugRenderSystem(),
            RenderSystem(),
        )

        start_column = board.columns // 2
        start_row = board.rows // 2

        grid_position = GridPosition(
            start_column,
            start_row,
        )
        initial_segment = self.factory.create(
            "segment",
            **segment_kwargs(board, grid_position),
        )

        self.factory.create("snake", segments=[initial_segment])

        queue.request_spawn("food")


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    """Create the reusable Snake application for desktop or browser hosts."""
    return TatuyApp(config)


def main() -> None:
    create_app({"engine": {"debug_overlay": True}}).run()


if __name__ == "__main__":
    main()

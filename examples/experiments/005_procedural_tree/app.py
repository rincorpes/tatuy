"""Seeded procedural trees. All experiment code lives in this module.

R: next seed; SPACE: regrow; P: pause; L: foliage; UP/DOWN: depth.
Generation uses local tree coordinates; presentation fits them to the viewport.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import cos, pi, sin
from random import Random

from tatuy import TatuyApp, TatuyConfigDict
from tatuy.ecs.world import World
from tatuy.geometry.size import Size
from tatuy.graphics.color import Color
from tatuy.graphics.render.queue import RenderQueue
from tatuy.input.frame import InputFrame
from tatuy.input.keys import Key
from tatuy.math.vec2 import Vec2
from tatuy.scenes.context import Intent, SceneContext, SceneTickContext
from tatuy.scenes.registry import SceneRegistry
from tatuy.scenes.scene import Scene


@dataclass(frozen=True)
class TreeSettings:
    """Dimensionless geometry settings, independent of window resolution."""

    depth: int = 8
    trunk_length: float = 120.0
    trunk_width: float = 22.0
    length_decay: float = 0.73
    width_decay: float = 0.67
    fork_angle: float = 0.48
    growth_duration: float = 4.0

    def __post_init__(self) -> None:
        if not 2 <= self.depth <= 10:
            raise ValueError("Tree depth must be between 2 and 10.")
        if min(self.trunk_length, self.trunk_width) <= 0:
            raise ValueError("Trunk dimensions must be positive.")
        if not 0 < self.length_decay < 1:
            raise ValueError("Length decay must be between zero and one.")
        if not 0 < self.width_decay < 1:
            raise ValueError("Width decay must be between zero and one.")
        if self.growth_duration <= 0:
            raise ValueError("Growth duration must be positive.")


@dataclass
class Branch:
    """A branch owns its children, retaining useful tree topology."""

    start: Vec2
    end: Vec2
    width: float
    depth: int
    children: list[Branch] = field(default_factory=list)

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()


@dataclass(frozen=True)
class Leaf:
    position: Vec2
    radius: float
    color: Color
    depth: int


@dataclass
class ProceduralTree:
    seed: int
    root: Branch
    leaves: tuple[Leaf, ...]
    branches: tuple[Branch, ...] = field(init=False)
    extent: tuple[float, float, float, float] = field(init=False)

    def __post_init__(self) -> None:
        self.branches = tuple(self.root.walk())
        # Include foliage and trunk thickness in the camera fit.
        xs = [p.x for b in self.branches for p in (b.start, b.end)]
        ys = [p.y for b in self.branches for p in (b.start, b.end)]
        for leaf in self.leaves:
            xs.extend((leaf.position.x - leaf.radius,
                       leaf.position.x + leaf.radius))
            ys.extend((leaf.position.y - leaf.radius,
                       leaf.position.y + leaf.radius))
        pad = self.root.width
        self.extent = (
            min(xs) - pad, min(ys) - pad,
            max(xs) + pad, max(ys) + pad,
        )


class TreeGenerator:
    """Generate geometry once, using an isolated reproducible RNG."""

    LEAF_COLORS = ((92, 145, 103), (124, 167, 111), (160, 185, 124))

    def __init__(self, settings: TreeSettings) -> None:
        self.settings = settings

    def generate(self, seed: int) -> ProceduralTree:
        rng = Random(seed)
        leaves: list[Leaf] = []
        root = self._branch(
            rng, leaves, Vec2.zero(), -pi / 2,
            self.settings.trunk_length, self.settings.trunk_width, 0,
        )
        return ProceduralTree(seed, root, tuple(leaves))

    def _branch(
        self, rng: Random, leaves: list[Leaf], start: Vec2,
        angle: float, length: float, width: float, depth: int,
    ) -> Branch:
        end = start + Vec2(cos(angle), sin(angle)) * length
        branch = Branch(start, end, width, depth)
        if depth == self.settings.depth:
            for _ in range(3):
                offset = Vec2(rng.uniform(-9, 9), rng.uniform(-7, 7))
                leaves.append(Leaf(
                    end + offset, rng.uniform(5, 10),
                    rng.choice(self.LEAF_COLORS), depth,
                ))
            return branch

        # Unequal forks avoid a perfectly mirrored fractal silhouette.
        for side in (-1, 1):
            spread = self.settings.fork_angle * rng.uniform(0.65, 1.35)
            direction = angle + side * spread + rng.uniform(-0.10, 0.10)
            # Mild upward tropism keeps the canopy from curling downward.
            direction += (-pi / 2 - direction) * 0.12
            branch.children.append(self._branch(
                rng, leaves, end, direction,
                length * self.settings.length_decay * rng.uniform(0.85, 1.1),
                width * self.settings.width_decay, depth + 1,
            ))
        return branch


class TreeGrowth:
    """Simulation state; rendering never advances growth."""

    def __init__(self, settings: TreeSettings, seed: int = 42) -> None:
        self.settings = settings
        self.seed = seed
        self.paused = False
        self.foliage = True
        self.age = 0.0
        self.tree = TreeGenerator(settings).generate(seed)

    def regenerate(self, seed: int, depth: int | None = None) -> None:
        from dataclasses import replace

        settings = self.settings
        if depth is not None:
            settings = replace(settings, depth=max(2, min(10, depth)))
        tree = TreeGenerator(settings).generate(seed)
        self.settings, self.seed, self.tree = settings, seed, tree
        self.age = 0.0

    def update(self, dt: float) -> None:
        if not self.paused:
            self.age = min(
                self.settings.growth_duration, self.age + max(0.0, dt)
            )

    def fraction(self, depth: int) -> float:
        stage = self.age / self.settings.growth_duration
        return max(0.0, min(1.0, stage * (self.settings.depth + 1) - depth))


class TreeRenderer:
    """Backend-independent presentation using Tatuy's render queue."""

    def draw(self, state: TreeGrowth, queue: RenderQueue,
             width: int, height: int) -> None:
        queue.rect(
            center=Vec2(width / 2, height / 2),
            size=Size(width, height), color=(23, 32, 37), z=-20,
        )
        left, top, right, bottom = state.tree.extent
        scale = max(0.001, min(
            width * 0.84 / (right - left),
            max(1, height - 135) / (bottom - top),
        ))
        origin = Vec2(
            width / 2 - (left + right) * scale / 2,
            height - 35 - bottom * scale,
        )
        queue.line(
            a=Vec2(width * 0.08, origin.y),
            b=Vec2(width * 0.92, origin.y),
            color=(65, 78, 72), thickness=2, z=-10,
        )
        for branch in state.tree.branches:
            amount = state.fraction(branch.depth)
            if amount <= 0:
                continue
            tip = branch.start + (branch.end - branch.start) * amount
            normal = Vec2(
                -(branch.end - branch.start).y,
                (branch.end - branch.start).x,
            ).normalized()
            base = normal * (branch.width / 2)
            taper = normal * (
                branch.width / 2 * (1 - 0.33 * amount)
            )
            points = [
                branch.start + base, tip + taper,
                tip - taper, branch.start - base,
            ]
            shade = min(190, 115 + branch.depth * 8)
            queue.poly(
                points=[origin + p * scale for p in points],
                fill=(shade, int(shade * 0.76), int(shade * 0.55)),
                stroke=None,
            )
            queue.circle(
                center=origin + branch.start * scale,
                radius=branch.width * scale / 2,
                color=(shade, int(shade * 0.76), int(shade * 0.55)),
            )
        if state.foliage:
            for leaf in state.tree.leaves:
                amount = state.fraction(leaf.depth)
                if amount > 0:
                    queue.circle(
                        center=origin + leaf.position * scale,
                        radius=leaf.radius * scale * amount,
                        color=leaf.color, z=1,
                    )
        queue.text(
            x=18, y=14,
            text=f"PROCEDURAL TREE | seed {state.seed} | "
                 f"depth {state.settings.depth} | "
                 f"{len(state.tree.branches)} branches",
            font_size=18, color=(221, 229, 211),
        )
        queue.text(
            x=18, y=40,
            text="R: new seed   SPACE: regrow   P: pause   "
                 "L: leaves   UP/DOWN: depth",
            font_size=14, color=(155, 175, 163),
        )


class MainWorld(World):
    pass


@dataclass
class MainIntent(Intent):
    regenerate: bool = False
    restart: bool = False
    pause: bool = False
    foliage: bool = False
    depth_delta: int = 0

    def update_from(self, input_frame: InputFrame) -> None:
        self.regenerate = input_frame.is_pressed(Key.R)
        self.restart = input_frame.is_pressed(Key.SPACE)
        self.pause = input_frame.is_pressed(Key.P)
        self.foliage = input_frame.is_pressed(Key.L)
        self.depth_delta = (
            int(input_frame.is_pressed(Key.UP))
            - int(input_frame.is_pressed(Key.DOWN))
        )


class MainContext(SceneTickContext[MainWorld, MainIntent]):
    @property
    def tree(self) -> TreeGrowth:
        return self.world.get_resource(TreeGrowth)


@SceneRegistry.implementation("main")
class MainScene(Scene[MainWorld, MainIntent, MainContext]):
    world_type = MainWorld
    intent_type = MainIntent
    tick_context_type = MainContext

    def resources(self, ctx: SceneContext):
        yield TreeGrowth(TreeSettings())

    def on_enter(self, ctx: SceneContext) -> None:
        self.renderer = TreeRenderer()

    def on_tick(self, ctx: MainContext) -> None:
        state, intent = ctx.tree, ctx.intent
        if intent.regenerate or intent.depth_delta:
            state.regenerate(
                state.seed + int(intent.regenerate),
                state.settings.depth + intent.depth_delta,
            )
        elif intent.restart:
            state.age = 0.0
        if intent.pause:
            state.paused = not state.paused
        if intent.foliage:
            state.foliage = not state.foliage
        state.update(ctx.dt)

    def on_present(self, ctx: MainContext) -> None:
        viewport = ctx.scene_context.viewport
        self.renderer.draw(
            ctx.tree, ctx.render_queue,
            viewport.virtual_w, viewport.virtual_h,
        )


def create_app(config: TatuyConfigDict | None = None) -> TatuyApp:
    """Create the reusable procedural-tree application."""
    return TatuyApp(config)


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()

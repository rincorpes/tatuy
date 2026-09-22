from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from tatuy.scenes.context import SceneContext
from tatuy.scenes.registry import SceneRegistry
from tatuy.scenes.scene import Scene

SceneFactory = Callable[[], Scene]


@dataclass(frozen=True)
class ScenePolicy:
    """
    Controls how a scene behaves in the scene stack.
    """

    blocks_update: bool = False
    blocks_input: bool = False
    is_opaque: bool = False
    receives_input: bool = True


@dataclass(frozen=True)
class SceneEntry:
    """
    An entry in the scene stack.
    """

    scene_id: str
    scene: Scene
    is_overlay: bool
    policy: ScenePolicy


@dataclass(frozen=True)
class StackItem:
    """
    An item in the scene stack.
    """

    entry: SceneEntry


class SceneService:

    def __init__(self):
        self._stack: list[StackItem] = []
        self._factories: dict[str, SceneFactory] = {}

    def register_factory(self, scene_id: str, factory: SceneFactory):
        self._factories[scene_id] = factory

    def contains(self, scene_id: str):
        return scene_id in self._factories or SceneRegistry.contains(scene_id)

    def change(self, scene_id: str, scene_context: SceneContext):
        if not self.contains(scene_id):
            print(f"Unknown scene: {scene_id}")
            return

        self.clean()
        self.push(scene_id, scene_context)

    def pop(self) -> SceneEntry | None:
        if not self._stack:
            return None

        item = self._stack.pop()
        item.entry.scene.on_exit()

        return item.entry

    def clean(self):
        while self._stack:
            self.pop()

    def push(
        self,
        scene_id: str,
        scene_context: SceneContext,
        *,
        is_overlay: bool = False,
        policy: ScenePolicy | None = None,
    ):
        policy = policy if policy is not None else ScenePolicy()

        factory = self._factories.get(scene_id)
        if factory is None:
            if not SceneRegistry.contains(scene_id):
                print(
                    f"No scene {scene_id}. Please add a scene and make sure it "
                    "is imported before running the engine"
                )
                return
            factory = SceneRegistry.get(scene_id)
        scene = factory()
        scene.on_enter(scene_context)
        self._stack.append(
            StackItem(
                entry=SceneEntry(
                    scene_id=scene_id,
                    scene=scene,
                    is_overlay=is_overlay,
                    policy=policy,
                )
            )
        )

    def visible_entries(self) -> list[SceneEntry]:
        """
        Render from bottom->top unless an opaque entry exists; if so,
            render only from that entry up.
        """
        entries = [i.entry for i in self._stack]
        # find highest opaque from top down; render starting there
        for idx in range(len(entries) - 1, -1, -1):
            if entries[idx].policy.is_opaque:
                return entries[idx:]
        return entries

    def input_entry(self) -> SceneEntry | None:
        """
        Who gets input this frame. If top blocks_input, only it receives input.
        If not, top still gets input (v1 simple). Later you can allow fall-through.

        :return: The SceneEntry that receives input, or None if no scenes are active.
        :rtype: SceneEntry | None
        """
        vis = self.visible_entries()
        if not vis:
            return None

        # If some scene blocks input, only scenes at/above it can receive.
        start_idx = 0
        for idx in range(len(vis) - 1, -1, -1):
            if vis[idx].policy.blocks_input:
                start_idx = idx
                break

        candidates = vis[start_idx:]

        # Pick the top-most candidate that actually receives input.
        for entry in reversed(candidates):
            if entry.policy.receives_input:
                return entry

        return None

    def update_entries(self) -> list[SceneEntry]:
        """
        Tick/update scenes considering blocks_update.
        Typical: pause overlay blocks update below it.
        """
        vis = self.visible_entries()
        if not vis:
            return []
        out = []
        for entry in reversed(vis):  # top->down
            out.append(entry)
            if entry.policy.blocks_update:
                break
        return list(reversed(out))  # bottom->top order

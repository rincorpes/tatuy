from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

from tatuy.audio.service import AudioService
from tatuy.capture.replay_header import ReplayHeader
from tatuy.commands import EngineCommandQueue
from tatuy.ecs.world import TWorld
from tatuy.graphics.canvas import Canvas
from tatuy.graphics.render.queue import RenderQueue
from tatuy.graphics.viewport.state import ViewportState
from tatuy.input.frame import InputFrame
from tatuy.resources import ResourceStore

TIntent = TypeVar("TIntent", bound="Intent")
TContext = TypeVar("TContext", bound="SceneTickContext")


@dataclass
class Intent:

    move_up: bool = False
    move_down: bool = False
    move_left: bool = False
    move_right: bool = False

    def update_from(self, input_frame: InputFrame):
        """
        Update the intent based on the input frame.
        """
        raise NotImplementedError(
            "update_from must be implemented in subclasses."
        )


@dataclass
class SceneContext:
    viewport: ViewportState
    audio: AudioService = field(kw_only=True)
    commands: EngineCommandQueue = field(default_factory=EngineCommandQueue)
    resources: ResourceStore = field(default_factory=ResourceStore)
    replay_header: ReplayHeader | None = None


@dataclass
class SceneTickContext(Generic[TWorld, TIntent]):
    dt: float
    world: TWorld
    intent: TIntent
    scene_context: SceneContext
    canvas: Canvas
    render_queue: RenderQueue

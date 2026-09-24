from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from tatuy.backend import Backend
from tatuy.capture.service import CaptureService
from tatuy.capture.settings import ReplaySettings
from tatuy.commands import (
    EngineCommand,
    EngineCommandQueue,
    Screenshot,
    StartRecording,
    StartReplay,
    StartVideoRecording,
    StopRecording,
    StopReplay,
    StopVideoRecording,
)
from tatuy.ecs.system import SystemPhase
from tatuy.engine.command_processor import EngineCommandProcessor
from tatuy.engine.loop.frame_packet import FramePacket
from tatuy.engine.pipelines import EnginePipelines
from tatuy.engine.render.compiler import compile_queue
from tatuy.engine.render.pipeline.pipeline import RenderPipeline
from tatuy.engine.runtime.services import RuntimeServices
from tatuy.engine.scene import SceneService
from tatuy.engine.system import SystemPipeline
from tatuy.events import EventCategory
from tatuy.events.bus import event_bus
from tatuy.geometry.size import Size
from tatuy.graphics.color import Color
from tatuy.graphics.render.context import RenderContext
from tatuy.graphics.render.queue import RenderQueue
from tatuy.graphics.viewport.service import ViewportService
from tatuy.input.frame import InputFrame
from tatuy.input.keys import Key
from tatuy.math.vec2 import Vec2
from tatuy.resources import ResourceStore
from tatuy.scenes.context import SceneContext
from tatuy.window.service import WindowService


@dataclass
class EngineConfig:
    start_scene: str = "main"
    fps: int = 60
    debug_overlay: bool = False

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> EngineConfig:
        return cls(**config)


class FrameInputCollector:
    def __init__(
        self,
        services: RuntimeServices,
    ) -> None:
        self._services = services

    def collect(self) -> InputFrame:
        events = self._services.events.get_event_frame()

        self._services.window.sync_events(events.get(EventCategory.WINDOW))

        self._services.input.sync_events(events.get(EventCategory.INPUT))

        return self._services.input.get_input_frame()


class SceneUpdater:
    def __init__(
        self,
        scene_service: SceneService,
        system_pipeline: SystemPipeline,
    ) -> None:
        self._scenes = scene_service
        self._systems = system_pipeline

    def update(
        self,
        dt: float,
        input_frame: InputFrame,
        scene_context: SceneContext,
    ) -> None:

        input_entry = self._scenes.input_entry()
        if not input_entry:
            print("No input entry")

        for entry in self._scenes.update_entries():
            effective_input = (
                input_frame if entry is input_entry else InputFrame()
            )

            scene = entry.scene
            queue = RenderQueue()
            canvas = QueuedCanvas(queue)

            if hasattr(scene, "intent"):
                scene.intent.update_from(effective_input)
            else:
                print("Not intent defined in Scene.")

            ctx = scene.create_tick_context(
                dt=dt,
                render_queue=queue,
                scene_context=scene_context,
                canvas=canvas,
            )
            scene.on_tick(ctx)

            # Custom system contexts are only needed when there are
            # systems participating in this phase.
            update_systems = [
                system
                for system in scene.systems
                if hasattr(scene, "systems")
                and system.phase in scene.UPDATE_PHASES
            ]

            if not update_systems:
                continue

            self._systems.step(
                scene.systems if hasattr(scene, "systems") else [],
                ctx,
                phases=(
                    SystemPhase.CONTROL,
                    SystemPhase.SIMULATION,
                ),
            )


class ScenePresenter:
    def __init__(
        self,
        scene_service: SceneService,
        system_pipeline: SystemPipeline,
    ) -> None:
        self._scenes = scene_service
        self._systems = system_pipeline

    def present(
        self,
        dt: float,
        scene_context: SceneContext,
    ) -> list[FramePacket]:

        packets: list[FramePacket] = []

        for entry in self._scenes.visible_entries():

            scene = entry.scene

            # One queue and one canvas for this scene's presentation.
            queue = RenderQueue()
            canvas = QueuedCanvas(queue)

            ctx = scene.create_tick_context(
                dt=dt,
                render_queue=queue,
                scene_context=scene_context,
                canvas=canvas,
            )
            scene.on_present(ctx)

            presentation_systems = [
                system
                for system in scene.systems
                if hasattr(scene, "systems")
                and system.phase in scene.PRESENTATION_PHASES
            ]

            if presentation_systems:
                system_context = scene.create_tick_context(
                    dt=dt,
                    render_queue=queue,
                    scene_context=scene_context,
                    canvas=canvas,
                )

                self._systems.step(
                    presentation_systems,
                    system_context,
                    phases=scene.PRESENTATION_PHASES,
                )

            packets.append(
                FramePacket(
                    scene_id=entry.scene_id,
                    is_overlay=entry.is_overlay,
                    packet=compile_queue(queue),
                )
            )

        return packets


class QueuedCanvas:
    """Record scene drawing commands into a render queue."""

    def __init__(self, queue: RenderQueue) -> None:
        self._queue = queue

    def rect(
        self,
        *,
        position: Vec2,
        size: Size,
        color: Color,
        radius: float = 0.0,
    ) -> None:
        # Canvas rectangles use a top-left position.
        # RenderQueue rectangles use a center.
        center = Vec2(
            position.x + size.width / 2,
            position.y + size.height / 2,
        )

        self._queue.rect(
            center=center,
            size=Size(size.width, size.height),
            color=color,
            radius=radius,
        )

    def circle(
        self,
        *,
        center: Vec2,
        radius: float,
        color: Color,
    ) -> None:
        self._queue.circle(
            center=center,
            radius=radius,
            color=color,
        )

    def text(
        self,
        *,
        position: Vec2,
        text: str,
        color: Color = (255, 255, 255),
        font_size: int | None = None,
        font_name: str | None = None,
    ) -> None:
        self._queue.text(
            x=position.x,
            y=position.y,
            text=text,
            color=color,
            font_size=font_size,
            font_name=font_name,
        )


class FrameRenderer:
    def __init__(
        self,
        backend: Backend,
        pipeline: RenderPipeline,
        viewport: ViewportService,
        window: WindowService,
        capture: CaptureService,
        *,
        debug_overlay: bool = False,
    ) -> None:
        self._backend = backend
        self._pipeline = pipeline
        self._viewport = viewport
        self._window = window
        self._capture = capture
        self._debug_overlay = debug_overlay

    def render(
        self,
        packets: list[FramePacket],
        dt: float,
    ) -> None:
        if not self._backend.initialized:
            return

        size = self._window.size
        self._viewport.resize(size)

        context = RenderContext(
            viewport=self._viewport.state,
            debug_overlay=self._debug_overlay,
            frame_ms=dt * 1000,
        )

        self._pipeline.render_frame_content(
            self._backend,
            context,
            packets,
        )

        self._capture.after_render()

        self._pipeline.present_frame(
            self._backend,
            context,
        )


class Engine:
    def __init__(
        self,
        backend: Backend,
        *,
        config: EngineConfig | None = None,
        resources: ResourceStore | None = None,
        pipelines: EnginePipelines | None = None,
        services: RuntimeServices | None = None,
    ):
        self._backend = backend
        self._resources = (
            resources if resources is not None else ResourceStore()
        )
        try:
            self.replay_settings = self._resources.get(ReplaySettings)
        except KeyError:
            self.replay_settings = ReplaySettings()

        self.config = config or EngineConfig()
        self.pipelines = pipelines or EnginePipelines()
        self.services = services or RuntimeServices.defaults(backend)

        self.frame_input_collector = FrameInputCollector(self.services)

        self.scene_updater: SceneUpdater
        self.scene_presenter: ScenePresenter
        self.frame_renderer = FrameRenderer(
            backend,
            self.pipelines.render,
            self.services.viewport,
            self.services.window,
            self.services.capture,
            debug_overlay=self.config.debug_overlay,
        )

        self.running = False
        self.scene_context: SceneContext

        self.commands = EngineCommandQueue()
        self.command_processor = EngineCommandProcessor(
            self,
            self._backend,
            self.commands,
        )

    def start(self):
        self.running = True
        event_bus.on("quit", self.stop)

        event_bus.on("windowmoved", self._debug_window_events)
        event_bus.on("windowresized", self._debug_window_events)
        event_bus.on("windowsizechanged", self._debug_window_events)
        event_bus.on("windowminimized", self._debug_window_events)
        event_bus.on("windowmaximized", self._debug_window_events)
        event_bus.on("windowrestored", self._debug_window_events)
        event_bus.on("windowclose", self._debug_window_events)

        self._backend.init()

        self.services.window.open()

        self.services.viewport.initialize(self.services.window.size)

        self.scene_context = SceneContext(
            viewport=self.services.viewport.state,
            audio=self.services.audio,
            commands=self.commands,
            resources=self._resources,
        )

        self.services.scene.change(
            self.config.start_scene,
            self.scene_context,
        )

        self.scene_updater = SceneUpdater(
            self.services.scene,
            self.pipelines.system,
        )
        self.scene_presenter = ScenePresenter(
            self.services.scene,
            self.pipelines.system,
        )

    def step(self, dt: float, _frame_index: int) -> None:
        if not self.running:
            return

        self.services.capture.poll()

        # Always poll live events, including during playback.
        # This preserves window close events and replay controls.
        live_input = self.frame_input_collector.collect()

        if not self.running:
            return

        self.services.viewport.resize(self.services.window.size)

        live_input = self._process_capture_hotkeys(live_input)

        if not self.running:
            return

        capture = self.services.capture
        header = capture.replay_header

        if header is not None:
            viewport = self.scene_context.viewport

            if (
                viewport.virtual_w != header.virtual_w
                or viewport.virtual_h != header.virtual_h
            ):
                raise ValueError(
                    "Window dimensions changed during the replay session"
                )

        simulation_dt = dt
        input_frame = live_input
        should_update = True

        if capture.replay_playing:
            recorded = capture.next_replay_frame()

            if recorded is None:
                # Keep presenting the final state without advancing it.
                simulation_dt = 0.0
                should_update = False
            else:
                input_frame = recorded.input_frame
                simulation_dt = recorded.dt

        if should_update:
            # Records exactly the input and timing consumed by the simulation.
            # The recorder does nothing when inactive.
            capture.record_input(input_frame, simulation_dt)

            self.scene_updater.update(
                dt=simulation_dt,
                input_frame=input_frame,
                scene_context=self.scene_context,
            )

        if not self.running:
            return

        self.command_processor.process()

        if not self.running:
            return

        packets = self.scene_presenter.present(
            dt=simulation_dt,
            scene_context=self.scene_context,
        )

        # Rendering diagnostics can still use the live frame duration.
        self.frame_renderer.render(packets, dt)

    def stop(self) -> None:
        if not self.running:
            return

        self.running = False

        try:
            self.services.capture.close()
        finally:
            self._backend.stop()
            event_bus.clear()

        print("Engine stopped.")

    def _debug_window_events(self, data):
        print(data)

    def _process_capture_hotkeys(
        self,
        live_input: InputFrame,
    ) -> InputFrame:
        capture = self.services.capture
        reserved: set[Key] = set()
        queued = False

        # Screenshot and video controls work independently of replay settings.
        if capture.settings.hotkeys_enabled:
            reserved.update({Key.F2, Key.F7, Key.F8})

            if live_input.is_pressed(Key.F2):
                self.commands.push(Screenshot())
                queued = True

            if live_input.is_pressed(Key.F8) and capture.video_recording:
                self.commands.push(StopVideoRecording())
                queued = True

            elif live_input.is_pressed(Key.F7) and not capture.video_busy:
                self.commands.push(StartVideoRecording())
                queued = True

        if self.replay_settings.enabled:
            reserved.update({Key.F3, Key.F4, Key.F5, Key.F6})

            filename = self.replay_settings.filename
            command: EngineCommand | None = None

            if live_input.is_pressed(Key.F6) and capture.replay_playing:
                command = StopReplay()

            elif live_input.is_pressed(Key.F4) and capture.replay_recording:
                command = StopRecording()

            elif live_input.is_pressed(Key.F5) and not capture.replay_playing:
                command = StartReplay(filename)

            elif (
                live_input.is_pressed(Key.F3)
                and not capture.replay_recording
                and not capture.replay_playing
            ):
                command = StartRecording(filename)

            if command is not None:
                # Scene-changing commands come last because they end the batch.
                self.commands.push(command)
                queued = True

        if queued:
            self.command_processor.process()

        return replace(
            live_input,
            keys_down=live_input.keys_down - reserved,
            keys_pressed=live_input.keys_pressed - reserved,
            keys_released=live_input.keys_released - reserved,
        )

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
from tatuy.engine.command_processor import EngineCommandProcessor
from tatuy.engine.loop.frame_packet import FramePacket
from tatuy.engine.pipelines import EnginePipelines
from tatuy.engine.render.compiler import compile_queue
from tatuy.engine.render.pipeline.pipeline import RenderPipeline
from tatuy.engine.runtime.services import RuntimeServices
from tatuy.engine.scene import SceneService
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
from tatuy.tooling.profiler import profiler
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
        with profiler.span("get_frame", "events"):
            events = self._services.events.get_event_frame()

        with profiler.span("window.sync", "events"):
            self._services.window.sync_events(events.get(EventCategory.WINDOW))

        with profiler.span("input.sync", "events"):
            self._services.input.sync_events(events.get(EventCategory.INPUT))

        return self._services.input.get_input_frame()


class SceneUpdater:
    def __init__(
        self,
        scene_service: SceneService,
    ) -> None:
        self._scenes = scene_service

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
            with profiler.span("screen_fx.update", "scene"):
                scene.screen_fx.update(dt)
            with profiler.span("camera_fx.update", "scene"):
                scene.camera_fx.update(dt)

            queue = RenderQueue()
            canvas = QueuedCanvas(queue)

            with profiler.span("intent.update_from_effective_input", "scene"):
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
            with profiler.span("on_tick", "scene"):
                scene.on_tick(ctx)
            with profiler.span(
                "system_pipeline.update",
                "scene",
                metadata={
                    "query_strategy": ctx.world.query_strategy.name,  # type: ignore
                },
            ):
                scene.system_pipeline.update(ctx)


class ScenePresenter:
    def __init__(
        self,
        scene_service: SceneService,
    ) -> None:
        self._scenes = scene_service

    def present(
        self,
        dt: float,
        scene_context: SceneContext,
    ) -> list[FramePacket]:

        packets: list[FramePacket] = []
        with profiler.span("scene.present", "scene"):
            for entry in self._scenes.visible_entries():

                scene = entry.scene

                # One queue and one canvas for this scene's presentation.
                queue = RenderQueue()
                canvas = QueuedCanvas(queue)

                with profiler.span("scene.create_trick_context", "scene"):
                    ctx = scene.create_tick_context(
                        dt=dt,
                        render_queue=queue,
                        scene_context=scene_context,
                        canvas=canvas,
                    )
                with profiler.span("scene.on_present", "scene"):
                    scene.on_present(ctx)

                with profiler.span(
                    "scene.system_pipeline.present",
                    "scene",
                    metadata={
                        "query_strategy": ctx.world.query_strategy.name,  # type: ignore
                    },
                ):
                    scene.system_pipeline.present(ctx)

                with profiler.span("compile_queue", "render_queue"):
                    packet = replace(
                        compile_queue(queue),
                        screen_overlays=scene.screen_fx.snapshot(),
                        world_view=scene.camera_fx.snapshot(),
                    )

                packets.append(
                    FramePacket(
                        scene_id=entry.scene_id,
                        is_overlay=entry.is_overlay,
                        packet=packet,
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

        with profiler.span("viewport.resize", "render"):
            size = self._window.size
            self._viewport.resize(size)

        context = RenderContext(
            viewport=self._viewport.state,
            debug_overlay=self._debug_overlay,
            frame_ms=dt * 1000,
        )

        with profiler.span("render_frame_content", "render"):
            self._pipeline.render_frame_content(
                self._backend,
                context,
                packets,
            )

        with profiler.span("capture.after_render", "render"):
            self._capture.after_render()

        with profiler.span("present_frame", "render"):
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

        self.services.scene.set_system_pipeline_factory(self.pipelines.system)

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
        self._capture_cleanup_pending = False
        self._backend_cleanup_pending = False
        self.scene_context: SceneContext

        self.commands = EngineCommandQueue()
        self.command_processor = EngineCommandProcessor(
            self,
            self._backend,
            self.commands,
        )

    def start(self):
        if not self.running and (
            self._capture_cleanup_pending or self._backend_cleanup_pending
        ):
            raise RuntimeError("Call stop() to finish cleanup before starting")

        self._capture_cleanup_pending = True
        self._backend_cleanup_pending = True
        self.running = True
        event_bus.on("quit", self.stop)

        event_bus.on("windowmoved", self._debug_window_events)
        event_bus.on("windowresized", self._debug_window_events)
        event_bus.on("windowsizechanged", self._debug_window_events)
        event_bus.on("windowminimized", self._debug_window_events)
        event_bus.on("windowmaximized", self._debug_window_events)
        event_bus.on("windowrestored", self._debug_window_events)
        event_bus.on("windowclose", self._debug_window_events)

        with profiler.trace("engine.start", "lifecycle"):
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
            )
            self.scene_presenter = ScenePresenter(
                self.services.scene,
            )

    def step(self, dt: float, frame_index: int) -> None:
        if not self.running:
            return
        with profiler.trace(
            "frame",
            "frame",
            metadata={
                "dt": dt,
                "frame": frame_index,
                "completed": False,
            },
        ) as frame_run:
            with profiler.span("events", "engine"):
                with profiler.span("capture.poll", "events"):
                    self.services.capture.poll()

                with profiler.span("input.collect", "events"):
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

                with profiler.span("scene.update", "scene"):
                    self.scene_updater.update(
                        dt=simulation_dt,
                        input_frame=input_frame,
                        scene_context=self.scene_context,
                    )

            if not self.running:
                return

            with profiler.span("commands", "engine"):
                self.command_processor.process()

            if not self.running:
                return

            with profiler.span("scene.present", "scene"):
                packets = self.scene_presenter.present(
                    dt=simulation_dt,
                    scene_context=self.scene_context,
                )

            with profiler.span("render", "render"):
                # Rendering diagnostics can still use the live frame duration.
                self.frame_renderer.render(packets, dt)

            if frame_run is not None:
                frame_run.metadata["completed"] = True

    def stop(self) -> None:
        """Stop execution and retry any unfinished resource cleanup.

        Capture closes before the backend is stopped. Successful stages are
        not repeated; failed stages remain pending even though running is
        false. Event subscriptions are cleared on every cleanup attempt.

        Returns:
            None: This method does not return a value.

        Raises:
            BaseException: Capture or backend cleanup fails. The failed stage
                remains pending for a later stop() call. If both fail, the
                backend error propagates with the capture error as context.
        """
        if not (
            self._capture_cleanup_pending or self._backend_cleanup_pending
        ):
            return

        with profiler.trace("engine.stop", "lifecycle"):
            self.running = False

            try:
                try:
                    if self._capture_cleanup_pending:
                        self.services.capture.close()
                        self._capture_cleanup_pending = False
                finally:
                    if self._backend_cleanup_pending:
                        self._backend.stop()
                        self._backend_cleanup_pending = False
            finally:
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

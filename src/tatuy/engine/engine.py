"""Core engine lifecycle and frame orchestration."""

from __future__ import annotations

from tatuy.backend import Backend
from tatuy.capture.settings import ReplaySettings
from tatuy.commands import EngineCommandQueue
from tatuy.engine.capture_input import CaptureInputProcessor
from tatuy.engine.command_processor import EngineCommandProcessor
from tatuy.engine.config import EngineConfig
from tatuy.engine.frame_input import FrameInputCollector
from tatuy.engine.pipelines import EnginePipelines
from tatuy.engine.render.renderer import FrameRenderer
from tatuy.engine.runtime.services import RuntimeServices
from tatuy.engine.scene_presentation import ScenePresenter
from tatuy.engine.scene_update import SceneUpdater
from tatuy.events.bus import event_bus
from tatuy.resources import ResourceStore
from tatuy.scenes.context import SceneContext
from tatuy.tooling.profiler import profiler


class Engine:
    """Coordinate engine lifecycle and per-frame execution."""

    def __init__(
        self,
        backend: Backend,
        *,
        config: EngineConfig | None = None,
        resources: ResourceStore | None = None,
        pipelines: EnginePipelines | None = None,
        services: RuntimeServices | None = None,
    ) -> None:
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
        self._replay_cleanup_pending = False
        self._capture_cleanup_pending = False
        self._backend_cleanup_pending = False
        self.scene_context: SceneContext

        self.commands = EngineCommandQueue()
        self.command_processor = EngineCommandProcessor(
            self,
            self._backend,
            self.commands,
        )
        self.capture_input_processor = CaptureInputProcessor(
            self.services.capture,
            self.services.replay,
            self.replay_settings,
            self.commands,
            self.command_processor,
        )

    def start(self) -> None:
        """Initialize backend services and enter the configured start scene."""
        if not self.running and (
            self._replay_cleanup_pending
            or self._capture_cleanup_pending
            or self._backend_cleanup_pending
        ):
            raise RuntimeError("Call stop() to finish cleanup before starting")

        self._replay_cleanup_pending = True
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

            self.scene_updater = SceneUpdater(self.services.scene)
            self.scene_presenter = ScenePresenter(self.services.scene)

    def step(self, dt: float, frame_index: int) -> None:
        """Execute one engine frame."""
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
                    live_input = self.frame_input_collector.collect()

            if not self.running:
                return

            self.services.viewport.resize(self.services.window.size)
            live_input = self.capture_input_processor.process(live_input)

            if not self.running:
                return

            replay = self.services.replay
            header = replay.header

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

            if replay.playing:
                recorded = replay.next_frame()

                if recorded is None:
                    simulation_dt = 0.0
                    should_update = False
                else:
                    input_frame = recorded.input_frame
                    simulation_dt = recorded.dt

            if should_update:
                replay.record_input(input_frame, simulation_dt)

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
                self.frame_renderer.render(packets, dt)

            if frame_run is not None and frame_run.metadata is not None:
                frame_run.metadata["completed"] = True

    def stop(self) -> None:
        """Stop execution and retry any unfinished resource cleanup.

        Replay and capture close before the backend is stopped. Successful
        stages are not repeated; failed stages remain pending even though
        running is false. Event subscriptions are cleared on every cleanup
        attempt.
        """
        if not (
            self._replay_cleanup_pending
            or self._capture_cleanup_pending
            or self._backend_cleanup_pending
        ):
            return

        with profiler.trace("engine.stop", "lifecycle"):
            self.running = False

            try:
                try:
                    try:
                        if self._replay_cleanup_pending:
                            self.services.replay.close()
                            self._replay_cleanup_pending = False
                    finally:
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

    def _debug_window_events(self, data) -> None:
        print(data)


__all__ = ["Engine", "EngineConfig", "EnginePipelines"]

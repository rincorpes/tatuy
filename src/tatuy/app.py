from __future__ import annotations

import gc
from dataclasses import dataclass
from typing import Any, TypedDict

from tatuy.audio.service import AudioService
from tatuy.backend.backend import Backend
from tatuy.backend.factory import BackendFactory
from tatuy.capture.contracts import CaptureCapability
from tatuy.capture.factory import create_capture_capability
from tatuy.capture.settings import (  # pylint: disable=unused-import
    CaptureSettings,
    ReplaySettingsBuilder,
)
from tatuy.engine.engine import Engine, EngineConfig, EnginePipelines
from tatuy.engine.runtime.bootstrap import (
    create_default_system_pipeline_factory,
)
from tatuy.engine.runtime.loop.asyncio_loop import AsyncioLoop
from tatuy.engine.runtime.loop.python_loop import PythonLoop
from tatuy.engine.runtime.runtime import AsyncRuntime, Runtime
from tatuy.engine.runtime.scene_composition import DefaultSceneInitializer
from tatuy.engine.runtime.services import RuntimeServices
from tatuy.engine.scene import SceneService
from tatuy.events.service import EventsService
from tatuy.graphics.viewport.service import ViewportService
from tatuy.input.service import InputService
from tatuy.resources import ResourceStore
from tatuy.settings import SettingsRegistry
from tatuy.tooling.profiler import profiler
from tatuy.tooling.profiler.export import export_profile
from tatuy.tooling.profiler.profiler import ProfilerConfig
from tatuy.window.service import WindowService


class ApplicationConfigDict(TypedDict, total=False):
    backend: str
    loop: str
    async_loop: str


class RuntimeCapabilitiesConfigDict(TypedDict, total=False):
    """Optional runtime capabilities selected by application composition."""

    capture: bool


class TatuyConfigDict(TypedDict, total=False):
    app: ApplicationConfigDict
    capabilities: RuntimeCapabilitiesConfigDict
    backend: dict[str, Any]
    engine: dict[str, Any]
    settings: dict[str, dict[str, Any]]
    profiler: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ApplicationConfig:
    backend: str = "pygame"
    loop: str = "python"
    async_loop: str = "asyncio"

    @classmethod
    def from_dict(cls, config: ApplicationConfigDict) -> ApplicationConfig:
        return cls(**config)


@dataclass(frozen=True, slots=True)
class RuntimeCapabilitiesConfig:
    """Select optional runtime capabilities while preserving desktop defaults."""

    capture: bool = True

    @classmethod
    def from_dict(
        cls,
        config: RuntimeCapabilitiesConfigDict,
    ) -> RuntimeCapabilitiesConfig:
        """Build capability selection from a configuration mapping."""
        return cls(**config)


class TatuyApp:

    _loop_types = {"python": PythonLoop}
    _async_loop_types = {"asyncio": AsyncioLoop}

    def __init__(
        self,
        config: TatuyConfigDict | None = None,
    ):
        self.config: TatuyConfigDict = config if config is not None else {}
        self.app_config = self._get_app_config(self.config or {})
        self.capabilities_config = self._get_capabilities_config(
            self.config or {}
        )
        self.resources = ResourceStore()

        self._build_settings()

        profiler_config = ProfilerConfig.from_dict(
            self.config.get("profiler", {})
        )
        profiler.configure(profiler_config)

    def _build_settings(self) -> None:
        sections = self.config.get("settings", {})

        if not isinstance(sections, dict):
            raise TypeError("The settings configuration must be a dictionary")
        sections = {
            "capture": {},
            **sections,
        }
        for name, values in sections.items():
            if not isinstance(values, dict):
                raise TypeError(
                    f"Settings section {name!r} must be a dictionary"
                )

            try:
                builder_type = SettingsRegistry.get(name)
            except KeyError as exc:
                raise ValueError(
                    f"No settings builder registered for {name!r}. "
                    "Import its module before creating TatuyApp."
                ) from exc

            try:
                settings = builder_type().build(dict(values))
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid settings section {name!r}: {exc}"
                ) from exc

            self.resources.add(settings)

    def _get_app_config(self, config: TatuyConfigDict) -> ApplicationConfig:
        app_config_dict = config.get("app")
        if app_config_dict is None:
            return ApplicationConfig()
        return ApplicationConfig.from_dict(app_config_dict)

    def _get_capabilities_config(
        self,
        config: TatuyConfigDict,
    ) -> RuntimeCapabilitiesConfig:
        capabilities_config_dict = config.get("capabilities")
        if capabilities_config_dict is None:
            return RuntimeCapabilitiesConfig()
        return RuntimeCapabilitiesConfig.from_dict(capabilities_config_dict)

    def create_backend(self) -> Backend:
        return BackendFactory.create(
            self.app_config.backend, self.config.get("backend", {})
        )

    def create_capture(self, backend: Backend) -> CaptureCapability:
        """Create the configured capture capability without changing defaults."""
        return create_capture_capability(
            backend,
            enabled=self.capabilities_config.capture,
            settings=self.resources.get(CaptureSettings),
        )

    def create_engine(self, backend: Backend) -> Engine:

        events_service = EventsService(backend)
        window_service = WindowService(backend)
        input_service = InputService(backend)
        capture_service = self.create_capture(backend)
        audio_service = AudioService(backend)

        return Engine(
            backend=backend,
            config=EngineConfig.from_dict(self.config.get("engine", {})),
            resources=self.resources,
            pipelines=EnginePipelines(),
            services=RuntimeServices(
                SceneService(
                    create_default_system_pipeline_factory(),
                    DefaultSceneInitializer().initialize,
                ),
                ViewportService(),
                events=events_service,
                window=window_service,
                input=input_service,
                capture=capture_service,
                audio=audio_service,
            ),
        )

    def get_loop(self) -> PythonLoop:
        """Build the configured synchronous runtime loop."""
        loop_type = self._loop_types.get(self.app_config.loop)

        if loop_type is None:
            raise ValueError(f"Unknown loop: {self.app_config.loop}")

        engine_config = EngineConfig.from_dict(self.config.get("engine", {}))

        return loop_type(target_fps=engine_config.fps)

    def get_async_loop(self) -> AsyncioLoop:
        """Build the configured asynchronous runtime loop."""
        loop_type = self._async_loop_types.get(self.app_config.async_loop)

        if loop_type is None:
            raise ValueError(
                f"Unknown async loop: {self.app_config.async_loop}"
            )

        return loop_type()

    def build(self) -> Runtime:
        """Build the default synchronous runtime without changing behavior."""
        backend = self.create_backend()
        engine = self.create_engine(backend)
        loop = self.get_loop()

        return Runtime(
            engine=engine,
            loop=loop,
        )

    def build_async(self) -> AsyncRuntime:
        """Build an opt-in asynchronous runtime for cooperative hosts."""
        backend = self.create_backend()
        engine = self.create_engine(backend)
        loop = self.get_async_loop()

        return AsyncRuntime(
            engine=engine,
            loop=loop,
        )

    def run(self) -> None:
        """Run Tatuy through the unchanged synchronous desktop path."""
        runtime = self.build()

        gc.disable()

        try:
            runtime.run()
        finally:
            self._finalize_run()

    async def run_async(self) -> None:
        """Run Tatuy through the explicitly selected asynchronous host path."""
        runtime = self.build_async()

        gc.disable()

        try:
            await runtime.run()
        finally:
            self._finalize_run()

    def _finalize_run(self) -> None:
        """Restore GC state and emit profiler output after either host path."""
        gc.collect()
        gc.enable()

        if profiler.enabled:
            snapshot = profiler.snapshot()

            export_profile(
                snapshot,
                ".tatuy/profiles/latest.json",
            )
            print(profiler.report())
            print("\nSlowest frames")
            print(profiler.format_slowest("frame", limit=3))
            print("Profile written to profiles/latest.json")

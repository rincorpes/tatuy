from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, TypedDict

from tatuy.audio.service import AudioService
from tatuy.backend.backend import Backend
from tatuy.backend.factory import BackendFactory
from tatuy.capture.contracts import CaptureCapability
from tatuy.capture.factory import create_capture_capability
from tatuy.capture.settings import (  # pylint: disable=unused-import
    CaptureSettings,
    ReplaySettings,
    ReplaySettingsBuilder,
)
from tatuy.engine.engine import Engine, EngineConfig, EnginePipelines
from tatuy.engine.runtime.bootstrap import (
    create_default_system_pipeline_factory,
)
from tatuy.engine.runtime.host import SyncRuntimeHost
from tatuy.engine.runtime.loop.asyncio_loop import AsyncioLoop
from tatuy.engine.runtime.loop.python_loop import PythonLoop
from tatuy.engine.runtime.runtime import Runtime, RuntimeLoopType, RuntimeMode
from tatuy.engine.runtime.scene_composition import DefaultSceneInitializer
from tatuy.engine.runtime.services import RuntimeServices
from tatuy.engine.scene import SceneService
from tatuy.events.service import EventsService
from tatuy.graphics.viewport.service import ViewportService
from tatuy.input.service import InputService
from tatuy.replay.contracts import ReplayCapability
from tatuy.replay.factory import create_replay_capability
from tatuy.resources import ResourceStore
from tatuy.settings import SettingsRegistry
from tatuy.tooling.profiler import profiler
from tatuy.tooling.profiler.profiler import ProfilerConfig
from tatuy.window.service import WindowService


class ApplicationConfigDict(TypedDict, total=False):
    backend: str
    loop: str


class RuntimeCapabilitiesConfigDict(TypedDict, total=False):
    """Optional runtime capabilities selected by application composition."""

    capture: bool
    replay: bool


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

    @classmethod
    def from_dict(cls, config: ApplicationConfigDict) -> ApplicationConfig:
        return cls(**config)


@dataclass(frozen=True, slots=True)
class LoopDefinition:
    """Describe how one configured loop is created and hosted."""

    mode: RuntimeMode
    factory: Callable[[EngineConfig], RuntimeLoopType]


def _create_python_loop(config: EngineConfig) -> PythonLoop:
    return PythonLoop(target_fps=config.fps)


def _create_asyncio_loop(config: EngineConfig) -> AsyncioLoop:
    del config
    return AsyncioLoop()


@dataclass(frozen=True, slots=True)
class RuntimeCapabilitiesConfig:
    """Select optional runtime capabilities while preserving desktop defaults."""

    capture: bool = True
    replay: bool = True

    @classmethod
    def from_dict(
        cls,
        config: RuntimeCapabilitiesConfigDict,
    ) -> RuntimeCapabilitiesConfig:
        """Build capability selection from a configuration mapping."""
        return cls(**config)


class TatuyApp:

    _loop_types = {
        "python": LoopDefinition("sync", _create_python_loop),
        "asyncio": LoopDefinition("async", _create_asyncio_loop),
    }

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
            "replay": {},
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

    def create_replay(self) -> ReplayCapability:
        """Create replay independently from screenshot/video capture."""
        return create_replay_capability(
            enabled=self.capabilities_config.replay,
            settings=self.resources.get(ReplaySettings),
        )

    def create_engine(self, backend: Backend) -> Engine:

        events_service = EventsService(backend)
        window_service = WindowService(backend)
        input_service = InputService(backend)
        capture_service = self.create_capture(backend)
        replay_service = self.create_replay()
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
                replay=replay_service,
                audio=audio_service,
            ),
        )

    def _get_loop_definition(self) -> LoopDefinition:
        definition = self._loop_types.get(self.app_config.loop)
        if definition is None:
            raise ValueError(f"Unknown loop: {self.app_config.loop}")
        return definition

    def get_loop(self) -> RuntimeLoopType:
        """Build the configured runtime loop."""
        definition = self._get_loop_definition()
        engine_config = EngineConfig.from_dict(self.config.get("engine", {}))
        return definition.factory(engine_config)

    def build(self) -> Runtime:
        """Build one runtime session from the configured backend and loop."""
        backend = self.create_backend()
        engine = self.create_engine(backend)
        definition = self._get_loop_definition()

        return Runtime(
            engine=engine,
            loop=definition.factory(engine.config),
            mode=definition.mode,
        )

    def run(self) -> None:
        """Run a synchronously configured Tatuy application."""
        runtime = self.build()
        SyncRuntimeHost().run(runtime)

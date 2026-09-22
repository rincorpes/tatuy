from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypedDict

from tatuy.audio.service import AudioService
from tatuy.backend.backend import Backend
from tatuy.backend.factory import BackendFactory
from tatuy.capture.service import CaptureService
from tatuy.capture.settings import CaptureSettings, ReplaySettingsBuilder
from tatuy.engine.engine import Engine, EngineConfig, EnginePipelines
from tatuy.engine.loop.python_loop import PythonLoop
from tatuy.engine.render.pipeline.pipeline import RenderPipeline
from tatuy.engine.runtime.runtime import Runtime
from tatuy.engine.runtime.services import RuntimeServices
from tatuy.engine.scene import SceneService
from tatuy.engine.system import SystemPipeline
from tatuy.events.service import EventsService
from tatuy.graphics.viewport.service import ViewportService
from tatuy.input.service import InputService
from tatuy.resources import ResourceStore
from tatuy.settings import SettingsRegistry
from tatuy.window.service import WindowService


class ApplicationConfigDict(TypedDict, total=False):
    backend: str
    loop: str


class TatuyConfigDict(TypedDict, total=False):
    app: ApplicationConfigDict
    backend: dict[str, Any]
    engine: dict[str, Any]
    settings: dict[str, dict[str, Any]]


@dataclass(frozen=True, slots=True)
class ApplicationConfig:
    backend: str = "pygame"
    loop: str = "python"

    @classmethod
    def from_dict(cls, config: ApplicationConfigDict) -> ApplicationConfig:
        return cls(**config)


class TatuyApp:

    _loop_types = {"python": PythonLoop}

    def __init__(
        self,
        config: TatuyConfigDict | None = None,
    ):
        self.config: TatuyConfigDict = config if config is not None else {}
        self.app_config = self._get_app_config(self.config or {})
        self.resources = ResourceStore()

        self._build_settings()

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

    def _get_app_config(self, config: TatuyConfigDict):
        app_config_dict = config.get("app")
        if app_config_dict is None:
            return ApplicationConfig()
        return ApplicationConfig.from_dict(app_config_dict)

    def create_backend(self) -> Backend:
        return BackendFactory.create(
            self.app_config.backend, self.config.get("backend", {})
        )

    def create_engine(self, backend: Backend) -> Engine:

        events_service = EventsService(backend)
        window_service = WindowService(backend)
        input_service = InputService(backend)
        capture_service = CaptureService(
            backend, settings=self.resources.get(CaptureSettings)
        )
        audio_service = AudioService(backend)

        return Engine(
            backend=backend,
            config=EngineConfig.from_dict(self.config.get("engine", {})),
            resources=self.resources,
            pipelines=EnginePipelines(
                system=SystemPipeline(), render=RenderPipeline()
            ),
            services=RuntimeServices(
                SceneService(),
                ViewportService(),
                events=events_service,
                window=window_service,
                input=input_service,
                capture=capture_service,
                audio=audio_service,
            ),
        )

    def get_loop(self):
        loop_type = self._loop_types.get(self.app_config.loop)

        if loop_type is None:
            raise ValueError(f"Unknown loop: {self.app_config.loop}")

        engine_config = EngineConfig.from_dict(self.config.get("engine", {}))

        return loop_type(target_fps=engine_config.fps)

    def build(self) -> Runtime:
        backend = self.create_backend()
        engine = self.create_engine(backend)
        loop = self.get_loop()

        return Runtime(
            engine=engine,
            loop=loop,
        )

    def run(self):
        runtime = self.build()
        runtime.loop.run(runtime.engine)

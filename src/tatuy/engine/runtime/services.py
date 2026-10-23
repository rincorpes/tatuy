from __future__ import annotations

from dataclasses import dataclass, field

from tatuy.audio.service import AudioService
from tatuy.backend.backend import Backend
from tatuy.capture.contracts import CaptureCapability
from tatuy.capture.factory import create_capture_capability
from tatuy.engine.runtime.bootstrap import (
    create_default_system_pipeline_factory,
)
from tatuy.engine.runtime.scene_composition import DefaultSceneInitializer
from tatuy.engine.scene import SceneService
from tatuy.events.service import EventsService
from tatuy.graphics.viewport.service import ViewportService
from tatuy.input.service import InputService
from tatuy.window.service import WindowService


def _default_scene_service() -> SceneService:
    return SceneService(
        create_default_system_pipeline_factory(),
        DefaultSceneInitializer().initialize,
    )


@dataclass
class RuntimeServices:
    scene: SceneService = field(default_factory=_default_scene_service)
    viewport: ViewportService = field(default=ViewportService())
    events: EventsService = field(kw_only=True)
    window: WindowService = field(kw_only=True)
    input: InputService = field(kw_only=True)
    capture: CaptureCapability = field(kw_only=True)
    audio: AudioService = field(kw_only=True)

    @classmethod
    def defaults(
        cls,
        backend: Backend,
        *,
        capture_enabled: bool = True,
    ) -> RuntimeServices:
        capture = create_capture_capability(
            backend,
            enabled=capture_enabled,
        )

        return cls(
            events=EventsService(backend),
            window=WindowService(backend),
            input=InputService(backend),
            capture=capture,
            audio=AudioService(backend),
        )

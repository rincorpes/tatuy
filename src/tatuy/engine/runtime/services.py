from __future__ import annotations

from dataclasses import dataclass, field

from tatuy.audio.service import AudioService
from tatuy.backend.backend import Backend
from tatuy.capture.service import CaptureService
from tatuy.engine.scene import SceneService
from tatuy.events.service import EventsService
from tatuy.graphics.viewport.service import ViewportService
from tatuy.input.service import InputService
from tatuy.window.service import WindowService


@dataclass
class RuntimeServices:
    scene: SceneService = field(default=SceneService())
    viewport: ViewportService = field(default=ViewportService())
    events: EventsService = field(kw_only=True)
    window: WindowService = field(kw_only=True)
    input: InputService = field(kw_only=True)
    capture: CaptureService = field(kw_only=True)
    audio: AudioService = field(kw_only=True)

    @classmethod
    def defaults(
        cls,
        backend: Backend,
    ) -> RuntimeServices:
        return cls(
            events=EventsService(backend),
            window=WindowService(backend),
            input=InputService(backend),
            capture=CaptureService(backend),
            audio=AudioService(backend),
        )

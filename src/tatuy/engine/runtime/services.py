from __future__ import annotations

from dataclasses import dataclass, field

from tatuy.assets.contracts import AssetProvider
from tatuy.assets.filesystem import FilesystemAssetProvider
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
from tatuy.replay.contracts import ReplayCapability
from tatuy.replay.factory import create_replay_capability
from tatuy.storage.contracts import StorageProvider
from tatuy.storage.filesystem import FilesystemStorageProvider
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
    replay: ReplayCapability = field(kw_only=True)
    audio: AudioService = field(kw_only=True)
    assets: AssetProvider = field(kw_only=True)
    storage: StorageProvider = field(kw_only=True)

    @classmethod
    def defaults(
        cls,
        backend: Backend,
        *,
        capture_enabled: bool = True,
        replay_enabled: bool = True,
        assets: AssetProvider | None = None,
        storage: StorageProvider | None = None,
    ) -> RuntimeServices:
        capture = create_capture_capability(
            backend,
            enabled=capture_enabled,
        )
        replay = create_replay_capability(enabled=replay_enabled)

        return cls(
            events=EventsService(backend),
            window=WindowService(backend),
            input=InputService(backend),
            capture=capture,
            replay=replay,
            audio=AudioService(backend),
            assets=assets or FilesystemAssetProvider(),
            storage=storage or FilesystemStorageProvider(),
        )

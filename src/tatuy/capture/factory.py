"""Compose enabled or disabled capture capabilities without eager tooling imports."""

from __future__ import annotations

from tatuy.backend.backend import Backend
from tatuy.capture.contracts import CaptureCapability
from tatuy.capture.null import NullCaptureService
from tatuy.capture.settings import CaptureSettings


def create_capture_capability(
    backend: Backend,
    *,
    enabled: bool = True,
    settings: CaptureSettings | None = None,
) -> CaptureCapability:
    """Create the configured capture capability while keeping capture lazy."""
    if not enabled:
        return NullCaptureService()

    # Lazy by design: disabled/browser hosts must not import capture workers/video.
    from tatuy.capture.service import (  # pylint: disable=import-outside-toplevel
        CaptureService,
    )

    return CaptureService(backend, settings=settings)

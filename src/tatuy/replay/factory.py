"""Compose enabled or disabled replay capabilities."""

from __future__ import annotations

from tatuy.capture.settings import ReplaySettings
from tatuy.replay.contracts import ReplayCapability
from tatuy.replay.null import NullReplayService
from tatuy.replay.service import ReplayService


def create_replay_capability(
    *,
    enabled: bool = True,
    settings: ReplaySettings | None = None,
) -> ReplayCapability:
    """Create the configured replay capability independently from capture."""
    if not enabled:
        return NullReplayService()
    return ReplayService(settings=settings)
    return ReplayService(settings=settings)

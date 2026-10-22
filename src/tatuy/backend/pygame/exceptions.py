"""Pygame-specific exception types within the shared backend hierarchy."""

from __future__ import annotations

from tatuy.backend.exceptions import BackendError


class PygameBackendError(BackendError):
    """Represent Pygame-specific failures catchable as BackendError."""

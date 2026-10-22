"""Shared exception root for backend-specific failures."""

from __future__ import annotations

from tatuy.exceptions import TatuyError


class BackendError(TatuyError):
    """Base error for failures reported by backend implementations."""

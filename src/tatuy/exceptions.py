from __future__ import annotations


class TatuyError(Exception):
    def __init__(self, message: str | None):
        prefix = self.__class__.__name__
        super().__init__(f"{prefix} - {message}" if message else prefix)

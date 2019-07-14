"""Implementation of the ``StderrSendChannel`` class."""

from __future__ import annotations

import sys

from typing import (
    Any)

from trio.abc import (
    SendChannel)


class StderrSendChannel(SendChannel[Any]):
    """A :class:`trio.abc.SendChannel` for writing to stderr."""

    async def send(
        self,
        value: Any
    ) -> None:
        """Write the specified value to stderr."""
        self.send_nowait(value)

    async def aclose(
        self
    ) -> None:
        pass

    def send_nowait(
        self,
        value: Any
    ) -> None:
        sys.stderr.write(str(value))
        sys.stderr.flush()

    def clone(
        self
    ) -> StderrSendChannel:
        return StderrSendChannel()

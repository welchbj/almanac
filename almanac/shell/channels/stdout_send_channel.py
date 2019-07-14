"""Implementation of the ``StdoutSendChannel`` class."""

from __future__ import annotations

import sys

from typing import (
    Any)

from trio.abc import (
    SendChannel)


class StdoutSendChannel(SendChannel[Any]):
    """A :class:`trio.abc.SendChannel` for writing to stdout."""

    async def send(
        self,
        value: Any
    ) -> None:
        """Write the specified value to stdout."""
        self.send_nowait(value)

    async def aclose(
        self
    ) -> None:
        pass

    def send_nowait(
        self,
        value: Any
    ) -> None:
        sys.stdout.write(str(value))
        sys.stdout.flush()

    def clone(
        self
    ) -> StdoutSendChannel:
        return StdoutSendChannel()

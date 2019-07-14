"""Implementation of the ``NullSendChannel`` class."""

from __future__ import annotations

from typing import (
    Any)

from trio.abc import (
    SendChannel)


class NullSendChannel(SendChannel[Any]):
    """A :class:`trio.abc.SendChannel` that doesn't send anything."""

    def send_nowait(
        self,
        value: Any
    ) -> None:
        pass

    async def aclose(
        self
    ) -> None:
        pass

    async def send(
        self,
        value: Any
    ) -> None:
        pass

    def clone(
        self
    ) -> NullSendChannel:
        return NullSendChannel()

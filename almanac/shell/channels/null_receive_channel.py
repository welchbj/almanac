"""Implementation of the ``NullReceiveChannel`` class."""

from __future__ import annotations

from typing import (
    Any)

from trio.abc import (
    ReceiveChannel)
from trio import (
    EndOfChannel)


class NullReceiveChannel(ReceiveChannel[Any]):
    """A :class:`trio.ReceiveChannel` that does not receive anything."""

    def receive(
        self
    ) -> Any:
        raise EndOfChannel()

    def receive_nowait(
        self
    ) -> Any:
        raise EndOfChannel()

    async def aclose(
        self
    ) -> None:
        pass

    def clone(
        self
    ) -> NullReceiveChannel:
        return NullReceiveChannel()

"""Implementation of the ``NullSendChannel`` class."""

from typing import (
    Any)

from trio.abc import (
    SendChannel)


class NullSendChannel(SendChannel[Any]):
    """A :class:``trio.abc.SendChannel`` that doesn't send anything."""

    async def send(
        self,
        value: Any
    ) -> None:
        pass

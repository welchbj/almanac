"""Implementation of the ``NullReceiveChannel`` class."""

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
        raise EndOfChannel

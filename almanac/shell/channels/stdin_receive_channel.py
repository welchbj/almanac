"""Implementation of the ``StdinReceiveChannel`` class."""

import sys

from trio.abc import (
    ReceiveChannel)
from trio import (
    EndOfChannel)


class StdinReceiveChannel(ReceiveChannel[str]):
    """A :class:`trio.abc.ReceiveChannel` for reading from stdin.

    Results will be yielded line-by-line.

    """

    async def receive(
        self
    ) -> str:
        line = next(sys.stdin, None)
        if line is None:
            raise EndOfChannel

        return line

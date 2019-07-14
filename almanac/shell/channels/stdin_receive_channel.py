"""Implementation of the ``StdinReceiveChannel`` class."""

from __future__ import annotations

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
        return self.receive_nowait()

    def receive_nowait(
        self
    ) -> str:
        line = next(sys.stdin, None)
        if line is None:
            raise EndOfChannel()

        return line

    async def aclose(
        self
    ) -> None:
        pass

    def clone(
        self
    ) -> StdinReceiveChannel:
        raise TypeError('StdinReceiveChannel is not clone()-able')

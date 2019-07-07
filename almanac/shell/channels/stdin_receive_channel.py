"""Implementation of the ``StdinReceiveChannel`` class."""

import sys

from trio.abc import (
    ReceiveChannel)
from trio import (
    sleep)


class StdinReceiveChannel(ReceiveChannel[str]):
    """A :class:``trio.abc.ReceiveChannel`` for reading from stdin.

    Results will be yielded line-by-line.

    """

    async def receive(
        self
    ) -> str:
        for line in sys.stdin:
            await sleep(0)
            yield line

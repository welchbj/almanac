"""Implementation of the ``StderrSendChannel`` class."""

import sys

from typing import (
    Any)

from trio.abc import (
    SendChannel)


class StderrSendChannel(SendChannel[Any]):
    """A :class:`trio.abc.SendChannel` for writing to stderr."""

    async def send(
        value: Any,
        end: str = '\n'
    ) -> None:
        """Write the specified value to stderr."""
        sys.stderr.write(str(value))
        sys.stderr.write(end)
        sys.stderr.flush()

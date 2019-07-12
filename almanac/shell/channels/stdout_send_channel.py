"""Implementation of the ``StdoutSendChannel`` class."""

import sys

from typing import (
    Any)

from trio.abc import (
    SendChannel)


class StdoutSendChannel(SendChannel[Any]):
    """A :class:`trio.abc.SendChannel` for writing to stdout."""

    async def send(
        value: Any,
        end: str = '\n'
    ) -> None:
        """Write the specified value to stdout."""
        sys.stdout.write(str(value))
        sys.stdout.write(end)
        sys.stdout.flush()

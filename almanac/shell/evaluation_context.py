"""Implementation of the ``EvaluationContext`` class."""

from __future__ import annotations

from typing import (
    Any,
    MutableMapping,
    Optional,
    Union)

from trio.abc import (
    ReceiveChannel,
    SendChannel)
from trio import (
    open_nursery)

from .channels import (
    NullReceiveChannel,
    NullSendChannel)


Channel = Union[SendChannel[Any], ReceiveChannel[Any]]


class EvaluationContext:
    """The context in which a part of an expression is evaluated.

    TODO: explain streams

    """

    def __init__(
        self,
        stdin: Optional[ReceiveChannel[Any]] = None,
        stdout: Optional[SendChannel[Any]] = None,
        stderr: Optional[SendChannel[Any]] = None
    ) -> None:
        self._stdin: ReceiveChannel[Any] = (stdin if stdin is not None
                                            else NullReceiveChannel())
        self._stdout: SendChannel[Any] = (stdout if stdout is not None
                                          else NullSendChannel())
        self._stderr: SendChannel[Any] = (stderr if stderr is not None
                                          else NullSendChannel())

        self._vars: MutableMapping[str, Any] = {}
        self._descriptors: MutableMapping[str, Channel] = {
            '0': self._stdin,
            'stdin': self._stdin,
            '1': self._stdout,
            'stdout': self._stdout,
            '2': self._stderr,
            'stderr': self._stderr
        }

    def clone(
        self
    ) -> EvaluationContext:
        """Clone a deep copy of this :class:`EvaluationContext`."""
        # TODO: how do we handle cloning of streams?

    @property
    def vars(
        self
    ) -> MutableMapping[str, Channel]:
        """A mapping of variable names to values."""
        return self._vars

    @property
    def descriptors(
        self
    ) -> MutableMapping[str, Any]:
        """A mapping of descriptor names to channel instances."""
        return self._descriptors

    @property
    def stdin(
        self
    ) -> ReceiveChannel[Any]:
        """The channel representing this context's stdin stream."""
        return self._stdin

    @property
    def stderr(
        self
    ) -> SendChannel[Any]:
        """The channel representing this context's stderr stream."""
        return self._stderr

    @property
    def stdout(
        self
    ) -> SendChannel[Any]:
        """The channel representing this context's stdout stream."""
        return self._stdout

    async def __aenter__(
        self
    ) -> None:
        """Call `__aenter__` on all of this context's descriptors."""
        with open_nursery() as nursery:
            for descriptor in self._descriptors.values():
                nursery.start_soon(descriptor.__aenter__)

    async def __aexit__(
        self
    ) -> None:
        """Call `__aclose__()` on all of this context's descriptors."""
        with open_nursery() as nursery:
            for descriptor in self._descriptors.values():
                nursery.start_soon(descriptor.__aexit__)

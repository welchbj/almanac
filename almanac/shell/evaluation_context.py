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
    StderrSendChannel,
    StdinReceiveChannel,
    StdoutSendChannel)


Channel = Union[SendChannel[Any], ReceiveChannel[Any]]


class EvaluationContext:
    """The context in which a part of an expression is evaluated.

    TODO: explain streams

    """

    def __init__(
        self,
        variables: MutableMapping[str, Any] = None,
        stdin: Optional[ReceiveChannel[Any]] = None,
        stdout: Optional[SendChannel[Any]] = None,
        stderr: Optional[SendChannel[Any]] = None
    ) -> None:
        self._stdin: ReceiveChannel[Any] = (stdin if stdin is not None
                                            else StdinReceiveChannel())
        self._stdout: SendChannel[Any] = (stdout if stdout is not None
                                          else StdoutSendChannel())
        self._stderr: SendChannel[Any] = (stderr if stderr is not None
                                          else StderrSendChannel())

        self._variables: MutableMapping[str, Any] = (
            variables if variables is not None else {})
        self._channels: MutableMapping[str, Channel] = {
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
        orig_stdin = self._stdin
        orig_stdout = self._stdout
        orig_stderr = self._stderr

        self._stdin = orig_stdin.clone()
        self._stdout = orig_stdout.clone()
        self._stderr = orig_stderr.clone()

        return EvaluationContext(
            variables=self._variables.copy(),
            stdin=orig_stdin.clone(),
            stdout=orig_stdout.clone(),
            stderr=orig_stderr.clone())

    @property
    def variables(
        self
    ) -> MutableMapping[str, Channel]:
        """A mapping of variable names to values."""
        return self._variables

    @property
    def channels(
        self
    ) -> MutableMapping[str, Any]:
        """A mapping of channel names to channel instances."""
        return self._channels

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
        """Call `__aenter__` on all of this context's channels."""
        with open_nursery() as nursery:
            for channel in self._channels.values():
                nursery.start_soon(channel.__aenter__)

    async def __aexit__(
        self
    ) -> None:
        """Call `__aclose__()` on all of this context's channel."""
        with open_nursery() as nursery:
            for channel in self._channels.values():
                nursery.start_soon(channel.__aexit__)

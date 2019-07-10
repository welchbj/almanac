"""Implementation of the ``EvaluationContext`` class."""

from __future__ import annotations

from typing import (
    Any,
    Optional)

from trio.abc import (
    ReceiveChannel,
    SendChannel)

from .channels import (
    NullReceiveChannel,
    NullSendChannel)

RecvAny = ReceiveChannel[Any]
SendAny = SendChannel[Any]


class EvaluationContext:
    """The context in which a part of an expression is evaluated.

    TODO: attributes

    """

    # TODO: how do we handle variable lookup?
    # TODO: how do we handle descriptor lookup?

    def __init__(
        self,
        stdin: Optional[RecvAny] = None,
        stdout: Optional[SendAny] = None,
        stderr: Optional[SendAny] = None
    ) -> None:
        self._stdin: RecvAny = (stdin if stdin is not None
                                else NullReceiveChannel())
        self._stdout: SendAny = (stdout if stdout is not None
                                 else NullSendChannel())
        self._stderr: SendAny = (stderr if stderr is not None
                                 else NullSendChannel())
        # TODO: initialization of descriptor and variable lookup tables

    def clone(
        self
    ) -> EvaluationContext:
        """Clone a deep copy of this ``EvaluationContext``."""
        # TODO: how do we handle cloning of streams?

    @property
    def stdin(
        self
    ) -> RecvAny:
        """The channel representing this context's stdin stream."""
        return self._stdin

    @property
    def stderr(
        self
    ) -> SendAny:
        """The channel representing this context's stderr stream."""
        return self._stderr

    @property
    def stdout(
        self
    ) -> SendAny:
        """The channel representing this context's stdout stream."""
        return self._stdout

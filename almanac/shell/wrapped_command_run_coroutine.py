"""Implementation of the ``WrappedCommandRunCoroutine`` class."""

from typing import (
    Any,
    Awaitable,
    Callable)

from .arguments import (
    AbstractShellArgument)
from .evaluation_context import (
    EvaluationContext)


class WrappedCommandRunCoroutine:
    """A wrapper around a :method:`AbstractCommand.run` coroutine."""

    def __init__(
        self,
        coro: Callable[..., Awaitable[Any]],
        evaluation_context: EvaluationContext,
        *args: AbstractShellArgument
    ) -> None:
        self._coro = coro
        self._evaluation_context = evaluation_context
        self._args = args

    async def __call__(
        self
    ) -> None:
        """Call the wrapped :class:`AbstractCommand.run` coroutine."""
        await self._coro(self._evaluation_context, *self._args)

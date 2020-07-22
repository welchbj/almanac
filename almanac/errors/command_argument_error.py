"""Exception type for improper command arguments."""

import inspect

from .almanac_error import AlmanacError


class CommandArgumentError(AlmanacError):
    """An exception type for improper command arguments."""

    # TODO: potential name change and tighter integration with BoundArguments

    def __init__(
        self,
        msg: str,
        arguments: inspect.BoundArguments
    ) -> None:
        super().__init__(msg)
        self._argument_state = arguments

    @property
    def argument_state(
        self
    ) -> inspect.BoundArguments:
        """The partially bound state from all valid arguments."""
        return self._argument_state

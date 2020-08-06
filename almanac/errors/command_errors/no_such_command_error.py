"""Exception type for non-existent command-name accesses."""

from typing import Tuple

from .base_command_error import BaseCommandError
from ..configuration_errors import BaseConfigurationError
from ..generic_errors import AlmanacKeyError


class NoSuchCommandError(BaseCommandError, BaseConfigurationError, AlmanacKeyError):
    """An exception type for resolutions of non-existent commands."""

    def __init__(
        self,
        *names: str
    ) -> None:
        if not names:
            msg = 'No such command with specified name.'
        elif len(names) == 1:
            msg = f'No such command with name {names[0]}.'
        elif len(names) == 2:
            msg = f'No commands exist with the name {names[0]} or {names[1]}.'
        else:
            joined_names = ','.join(names[:-1]) + f', or {names[-1]}'
            msg = f'No commands exist with the name {joined_names}.'

        super().__init__(msg)
        self._names = names

    @property
    def names(
        self
    ) -> Tuple[str, ...]:
        """A tuple of the command names that spawned this error."""
        return self._names

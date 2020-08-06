"""Exception type for non-existent argument-name accesses."""

from typing import Tuple

from .base_argument_error import BaseArgumentError
from ..generic_errors import AlmanacKeyError


class NoSuchArgumentError(BaseArgumentError, AlmanacKeyError):
    """An exception type for resolutions of non-existent arguments."""

    def __init__(
        self,
        *names: str
    ) -> None:
        if not names:
            msg = 'No such argument with specified name.'
        elif len(names) == 1:
            msg = f'No such argument with name {names[0]}.'
        elif len(names) == 2:
            msg = f'No arguments exist with the name {names[0]} or {names[1]}.'
        else:
            joined_names = ','.join(names[:-1]) + f', or {names[-1]}'
            msg = f'No arguments exist with the name {joined_names}.'

        super().__init__(msg)
        self._names = names

    @property
    def names(
        self
    ) -> Tuple[str, ...]:
        """A tuple of the argument names that triggered this error."""
        return self._names

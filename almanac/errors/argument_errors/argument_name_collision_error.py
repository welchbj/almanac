"""Exception type for argument name collisions."""

from typing import Tuple

from .base_argument_error import BaseArgumentError


class ArgumentNameCollisionError(BaseArgumentError):
    """An exception type for when argument names would collide."""

    def __init__(
        self,
        *names: str
    ) -> None:
        if not names:
            msg = 'Cannot map multiple arguments with the same identifier'
        elif len(names) == 1:
            msg = f'Cannot map multiple arguments with the same identifer {names[0]}'
        elif len(names) == 2:
            msg = (
                'Cannot map multiple arguments with the same identifiers '
                f'{names[0]} and {names[1]}'
            )
        else:
            joined_names = ','.join(names[:-1]) + f', and {names[-1]}'
            msg = f'Cannot map multiple arguments the same identifiers {joined_names}'

        super().__init__(msg)
        self._names = names

    @property
    def names(
        self
    ) -> Tuple[str, ...]:
        """A tuple of the argument names that spawned this error."""
        return self._names

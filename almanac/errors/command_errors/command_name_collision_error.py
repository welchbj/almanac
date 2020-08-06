"""Exception type for command name collisions."""

from typing import Tuple

from .base_command_error import BaseCommandError


class CommandNameCollisionError(BaseCommandError):
    """An exception type for when command names would collide."""

    def __init__(
        self,
        *names: str
    ) -> None:
        if not names:
            msg = 'Cannot map multiple commands with the same identifier'
        elif len(names) == 1:
            msg = f'Cannot map multiple commands with the same identifer {names[0]}'
        elif len(names) == 2:
            msg = (
                'Cannot map multiple commands with the same identifiers '
                f'{names[0]} and {names[1]}'
            )
        else:
            joined_names = ','.join(names[:-1]) + f', and {names[-1]}'
            msg = f'Cannot map multiple commands the same identifiers {joined_names}'

        super().__init__(msg)
        self._names = names

    @property
    def names(
        self
    ) -> Tuple[str, ...]:
        """A tuple of the command names that spawned this error."""
        return self._names

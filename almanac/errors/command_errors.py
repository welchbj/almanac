from typing import Tuple

from almanac.errors.almanac_error import AlmanacError
from almanac.errors.configuration_errors import BaseConfigurationError
from almanac.errors.generic_errors import AlmanacKeyError


class BaseCommandError(AlmanacError):
    """The base exception type for command-related errors."""


class CommandNameCollisionError(BaseCommandError):
    """An exception type for when command names would collide."""

    def __init__(self, *names: str) -> None:
        if not names:
            msg = "Cannot map multiple commands with the same identifier."
        elif len(names) == 1:
            msg = f"Cannot map multiple commands with the same identifer {names[0]}."
        elif len(names) == 2:
            msg = (
                "Cannot map multiple commands with the same identifiers "
                f"{names[0]} and {names[1]}."
            )
        else:
            joined_names = ",".join(names[:-1]) + f", and {names[-1]}"
            msg = f"Cannot map multiple commands the same identifiers {joined_names}."

        super().__init__(msg)
        self._names = names

    @property
    def names(self) -> Tuple[str, ...]:
        """A tuple of the command names that spawned this error."""
        return self._names


class CommandRegistrationError(BaseCommandError):
    """An exception type for invalid command registration."""


class NoSuchCommandError(BaseCommandError, BaseConfigurationError, AlmanacKeyError):
    """An exception type for resolutions of non-existent commands."""

    def __init__(self, *names: str) -> None:
        if not names:
            msg = "No such command with specified name."
        elif len(names) == 1:
            msg = f"No such command with name {names[0]}."
        elif len(names) == 2:
            msg = f"No commands exist with the name {names[0]} or {names[1]}."
        else:
            joined_names = ",".join(names[:-1]) + f", or {names[-1]}"
            msg = f"No commands exist with the name {joined_names}."

        super().__init__(msg)
        self._names = names

    @property
    def names(self) -> Tuple[str, ...]:
        """A tuple of the command names that spawned this error."""
        return self._names

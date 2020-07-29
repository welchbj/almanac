"""Exception type for command registration errors."""

from .base_command_error import BaseCommandError


class CommandRegistrationError(BaseCommandError):
    """An exception type for invalid command registration."""
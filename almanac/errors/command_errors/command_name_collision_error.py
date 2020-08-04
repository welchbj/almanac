"""Exception type for command name collisions."""

from .base_command_error import BaseCommandError


class CommandNameCollisionError(BaseCommandError):
    """An exception type for when command names would collide."""

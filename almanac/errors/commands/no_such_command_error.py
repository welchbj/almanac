"""Exception type for non-existent command-name accesses."""

from .base_command_error import BaseCommandError


class NoSuchCommandError(BaseCommandError, KeyError):
    """An exception type for resolutions of non-existent commands."""

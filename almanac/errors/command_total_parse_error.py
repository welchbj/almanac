"""Exception type for when command parsing totally fails."""

from .command_parse_error import CommandParseError


class CommandTotalParseError(CommandParseError):
    """Exception type for when command parsing totally fails."""

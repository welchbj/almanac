"""Base class for command-parsing errors."""

from .almanac_error import AlmanacError


class CommandParseError(AlmanacError):
    """The base class exception type for parser-related errors."""

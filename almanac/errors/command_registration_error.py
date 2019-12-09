"""Exception type for command registration errors."""

from .almanac_error import (
    AlmanacError)


class CommandRegistrationError(AlmanacError):
    """An exception type for invalid command registration."""

"""Exception type for non-existent command-name accesses."""

from .almanac_error import AlmanacError


class NoSuchCommandError(AlmanacError, KeyError):
    """An exception type for resolutions of non-existent commands."""

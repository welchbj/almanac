"""Exception type for non-existent argument-name accesses."""

from .base_argument_error import BaseArgumentError


class NoSuchArgumentError(BaseArgumentError, KeyError):
    """An exception type for resolutions of non-existent arguments."""

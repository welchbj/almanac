"""Exception type for too many positional arguments being specified."""

from .base_argument_error import BaseArgumentError


class TooManyPositionalArgumentsError(BaseArgumentError):
    """An exception type for when too many positional arguments are specified."""

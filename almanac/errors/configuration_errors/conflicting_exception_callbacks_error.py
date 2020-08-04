"""Exception type for trying to implicitly overwrite an exception hook callback."""

from ..almanac_error import AlmanacError


class ConflictingExceptionCallbacksError(AlmanacError):
    """Exception type for trying to implicitly overwrite an exception hook callback."""

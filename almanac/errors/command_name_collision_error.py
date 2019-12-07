"""Exception type for command name collisions."""

from .almanac_error import (
    AlmanacError)


class CommandNameCollisionError(AlmanacError):
    """An exception type for when command names would collide."""

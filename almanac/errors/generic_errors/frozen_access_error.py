from ..almanac_error import AlmanacError


class FrozenAccessError(AlmanacError):
    """An exception type for invalid accesses on frozen objects."""

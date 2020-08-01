"""Exception type for attempting to map multiple promoters to one type."""

from ..almanac_error import AlmanacError


class ConflictingPromoterTypesError(AlmanacError):
    """An exception type for attempting to map multiple promoters to one type."""

from almanac.errors.almanac_error import AlmanacError


class NoActiveApplicationError(AlmanacError):
    """An exception type for when context methods are called without an active app."""

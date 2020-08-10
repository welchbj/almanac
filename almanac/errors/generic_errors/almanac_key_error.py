from ..almanac_error import AlmanacError


class AlmanacKeyError(AlmanacError, KeyError):
    """A subclass of KeyError that does not surround exception messages with quotes."""

    def __str__(
        self
    ) -> str:
        return str(self.args[0])

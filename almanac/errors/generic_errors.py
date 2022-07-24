from almanac.errors.almanac_error import AlmanacError


class AlmanacKeyError(AlmanacError, KeyError):
    """A subclass of KeyError that does not surround exception messages with quotes."""

    def __str__(self) -> str:
        return str(self.args[0])


class FrozenAccessError(AlmanacError):
    """An exception type for invalid accesses on frozen objects."""


class PositionalValueError(ValueError, AlmanacError):
    """An exception that holds a specific, error-causing input position."""

    def __init__(self, msg: str, error_pos: int) -> None:
        super().__init__(msg)
        self._error_pos = error_pos

    @property
    def error_pos(self) -> int:
        """The zero-based index of an error-causing position."""
        return self._error_pos

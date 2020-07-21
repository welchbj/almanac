"""Implementation of the ``PositionalValueError`` class."""

from .almanac_error import AlmanacError


class PositionalValueError(ValueError, AlmanacError):
    """An exception that holds a specific, error-causing input position."""

    def __init__(
        self,
        msg: str,
        error_pos: int
    ) -> None:
        super().__init__(msg)
        self._error_pos = error_pos

    @property
    def error_pos(
        self
    ) -> int:
        """The zero-based index of an error-causing position."""
        return self._error_pos

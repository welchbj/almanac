import pyparsing as pp

from almanac.errors.almanac_error import AlmanacError
from almanac.errors.generic_errors import PositionalValueError


class BaseParseError(AlmanacError):
    """The base class exception type for parser-related errors."""


class PartialParseError(BaseParseError, PositionalValueError):
    """An exception type for when command parsing partially fails."""

    def __init__(
        self,
        msg: str,
        remaining: str,
        partial_result: pp.ParseResults,
        col: int,
    ) -> None:
        super().__init__(msg, col - 1)

        self.remaining = remaining
        self.partial_result = partial_result
        self.col = col


class TotalParseError(BaseParseError):
    """Exception type for when command parsing totally fails."""

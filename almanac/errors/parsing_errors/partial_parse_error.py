import pyparsing as pp

from .base_parse_error import BaseParseError
from ..generic_errors import PositionalValueError


class PartialParseError(BaseParseError, PositionalValueError):
    """An exception type for when command parsing partially fails."""

    def __init__(
        self,
        msg: str,
        remaining: str,
        partial_result: pp.ParseResults,
        col: int,
    ) -> None:
        super().__init__(msg, col-1)

        self.remaining = remaining
        self.partial_result = partial_result
        self.col = col

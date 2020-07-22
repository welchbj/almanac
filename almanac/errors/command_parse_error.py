"""Exception type for command parsing errors."""

import pyparsing as pp

from .positional_value_error import PositionalValueError


class CommandParseError(PositionalValueError):
    """An exception type for when command parsing fails."""

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

"""Exception type for command parsing errors."""

import pyparsing as pp

from .almanac_error import AlmanacError


class CommandParseError(AlmanacError):
    """An exception type for when command parsing fails."""

    def __init__(
        self,
        msg: str,
        remaining: str,
        partial_result: pp.ParseResults,
        col: int,
    ) -> None:
        super().__init__(msg)

        self.remaining = remaining
        self.partial_result = partial_result
        self.col = col

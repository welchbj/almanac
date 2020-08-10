from .base_parse_error import BaseParseError


class TotalParseError(BaseParseError):
    """Exception type for when command parsing totally fails."""

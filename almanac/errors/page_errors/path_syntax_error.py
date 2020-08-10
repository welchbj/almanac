from .base_page_error import BasePageError
from ..generic_errors import PositionalValueError


class PathSyntaxError(BasePageError, PositionalValueError):
    """An exception type for path syntax errors."""

"""Implementation of the ``Shtate`` class."""

from enum import (
    auto,
    Enum)


class Shtate(Enum):
    """``Shlexer`` + state = ``Shtate``."""
    ENTER_NEW_CONTEXT = auto()

    IN_COMMAND_NAME = auto()
    IN_COMMAND_BODY = auto()

    EXPECTING_FILE_DESCRIPTOR = auto()
    IN_FILE_DESCRIPTOR = auto()

    EXPECTING_HEREDOC_BEGIN = auto()
    IN_HEREDOC = auto()

    IN_HERESTR = auto()

    IN_QUOTE_ALLOW_EXPANSION_BLOCK = auto()
    IN_QUOTE_DISALLOW_EXPANSION_BLOCK = auto()

    ESCAPE_NEXT = auto()

    PARSE_FAILED = auto()
    PARSE_SUCCEEDED = auto()

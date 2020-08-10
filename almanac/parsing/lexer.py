from __future__ import annotations

import re

from typing import Iterator, Tuple, Type, TypeVar, TYPE_CHECKING

from pygments.lexer import RegexLexer, bygroups
from pygments.token import (
    Name,
    Keyword,
    Number,
    Operator,
    Text,
    Token,
    String
)

from .parsing import Patterns

if TYPE_CHECKING:
    from ..core import Application, CommandEngine


_T = TypeVar('_T')


class _with_app:
    def __init__(
        self,
        app: Application
    ) -> None:
        self._app = app

    def __call__(
        self,
        cls: Type[_T]
    ) -> Type[_T]:
        setattr(cls, 'app', self._app)
        return cls


def _resolve_command(lexer, match) -> Iterator[Tuple[int, Token, str]]:
    """Pygments lexer callback for determining if a command is valid.

    Yielded values take the form: (index, tokentype, value).

    See:
        https://pygments.org/docs/lexerdevelopment/#callbacks

    """
    command_engine: CommandEngine = lexer.app.command_engine
    command_name = match.group(0)

    if command_name.strip() in command_engine.keys():
        token_type = Name.RealCommand
    else:
        token_type = Name.NonexistentCommand

    yield match.start(), token_type, command_name


def get_lexer_cls_for_app(
    app: Application
) -> Type[RegexLexer]:
    """Get a lexer class for a specific Application instance."""

    @_with_app(app)
    class _Lexer(RegexLexer):
        """A lexer for almanac command lines.

        See:
            https://pygments.org/docs/lexerdevelopment/

        """

        name = 'almanac lexer'
        flags = re.IGNORECASE

        tokens = {
            'root': [
                (Patterns.WHITESPACE, Text),

                (Patterns.BOOLEAN, Keyword.Boolean),
                (Patterns.INTEGER, Number.Integer),
                (Patterns.FLOAT, Number.Float),

                (Patterns.STRING_SINGLE_QUOTE, String.SingleQuote),
                (Patterns.STRING_DOUBLE_QUOTE, String.DoubleQuote),

                (Patterns.KWARG, bygroups(Name.Kwarg, Operator)),
                (Patterns.COMMAND, _resolve_command),
            ]
        }

    return _Lexer

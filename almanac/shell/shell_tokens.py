"""Implementation of the ``ShellTokens`` class."""

from typing import (
    Tuple)


class ShellTokens:
    """Tokens for shell lexing and parsing."""

    HERESTR_BEGIN_TOKEN: str = '<<<'
    HEREDOC_BEGIN_TOKEN: str = '<<'

    OUTPUT_STREAM_REDIR_TOKEN: str = '>'
    INPUT_STREAM_REDIR_TOKEN: str = '<'

    FILE_DESCRIPTOR_BEGIN_TOKEN: str = '%'
    VARIABLE_BEGIN_TOKEN: str = '$'

    PAREN_OPEN_TOKEN: str = '('
    PAREN_CLOSE_TOKEN: str = ')'

    QUOTE_ALLOW_EXPANSION_BEGIN_TOKEN: str = '"'
    QUOTE_NO_EXPANSION_BEGIN_TOKEN: str = "'"

    PIPE_TOKEN: str = '|'

    CHAIN_COMMAND_LAST_FAILED_TOKEN: str = '&&'
    CHAIN_COMMAND_LAST_PASSED_TOKEN: str = '||'
    CHAIN_COMMAND_LAST_ANY_TOKEN: str = '&'

    LINE_DELIM_TOKENS: Tuple[str, ...] = ('\n',)
    WHITESPACE_TOKENS: Tuple[str, ...] = (' ', '\t', '\r',)

    ESCAPE_TOKENS: Tuple[str, ...] = ('\\',)

    SYMBOL_TOKENS: Tuple[str, ...] = tuple(sorted((
        HERESTR_BEGIN_TOKEN,
        HEREDOC_BEGIN_TOKEN,
        OUTPUT_STREAM_REDIR_TOKEN,
        INPUT_STREAM_REDIR_TOKEN,
        FILE_DESCRIPTOR_BEGIN_TOKEN,
        VARIABLE_BEGIN_TOKEN,
        PAREN_OPEN_TOKEN,
        PAREN_CLOSE_TOKEN,
        QUOTE_ALLOW_EXPANSION_BEGIN_TOKEN,
        QUOTE_NO_EXPANSION_BEGIN_TOKEN,
        PIPE_TOKEN,
        CHAIN_COMMAND_LAST_FAILED_TOKEN,
        CHAIN_COMMAND_LAST_PASSED_TOKEN,
        CHAIN_COMMAND_LAST_ANY_TOKEN,),
        key=len,
        reverse=True))

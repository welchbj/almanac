from typing import Optional, Type

from pygments import highlight
from pygments.formatter import Formatter
from pygments.formatters import TerminalFormatter
from pygments.lexers import get_lexer_for_mimetype
from pygments.util import ClassNotFound


def highlight_for_mimetype(
    text: str,
    mimetype: str,
    *,
    fallback_mimetype: Optional[str] = 'text/plain',
    formatter_cls: Type[Formatter] = TerminalFormatter
) -> str:
    """Return ANSI-escaped highlighted text, as per the .

    If :param`mimetype` cannot be resolved, then :param`fallback_mimetype` will be used.
    If that cannot be resolved (or is ``None``), then the pygments ``ClassNotFound``
    exception will be raised.

    """
    try:
        lexer = get_lexer_for_mimetype(mimetype)
    except ClassNotFound as e:
        if fallback_mimetype is not None:
            lexer = get_lexer_for_mimetype(fallback_mimetype)
        else:
            raise e

    highlighted_text: str = highlight(text, lexer, formatter_cls())
    return highlighted_text

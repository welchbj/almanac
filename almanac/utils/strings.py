"""String utilities."""

import textwrap

from ..constants import CommandLineDefaults


def capitalized(
    text: str
) -> str:
    """Capitalize the first letter of the text."""
    if not text:
        return text

    return text[0].upper() + text[1:]


def abbreviated(
    text: str,
    len: int = CommandLineDefaults.MAX_COMPLETION_WIDTH,
    placeholder: str = '...'
) -> str:
    """Abbreviate the text to the specified length."""
    return textwrap.shorten(text, width=len, placeholder=placeholder)

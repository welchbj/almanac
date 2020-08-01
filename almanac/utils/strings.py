"""String utilities."""


def capitalized(
    text: str
) -> str:
    """Capitalize the first letter of the text."""
    if not text:
        return text

    return text[0].upper() + text[1:]

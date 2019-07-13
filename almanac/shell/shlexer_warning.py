"""Implementation of the ``ShlexerWarning`` class."""

from typing import (
    Optional)


class ShlexerWarning:
    """Encapsulation of a warning that occured during ``Shlexer`` parsing."""

    def __init__(
        self,
        message: str,
        source: str,
        position: Optional[int],
        is_fatal: bool = False
    ) -> None:
        self._message: str = message
        self._source: str = source
        self._position: Optional[int] = position
        self._is_fatal: bool = is_fatal

    @property
    def message(
        self
    ) -> str:
        """The user-friendly warning message."""
        return self._message

    @property
    def source(
        self
    ) -> str:
        """The source string that generate the warning."""
        return self._source

    @property
    def position(
        self
    ) -> Optional[int]:
        """The zero-based position (if there is one) tied to the warning."""
        return self._position

    @property
    def is_fatal(
        self
    ) -> bool:
        """Whether this warning will cause execution to fail."""
        return self._is_fatal

    # TODO: __str__ / __repr__

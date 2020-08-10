from __future__ import annotations

from typing import TYPE_CHECKING

from .almanac_error import AlmanacError
from .generic_errors import AlmanacKeyError, PositionalValueError

if TYPE_CHECKING:
    from ..pages import PagePathLike


class BasePageError(AlmanacError):
    """Base error for all page-based errors."""


class BlockedPageOverwriteError(BasePageError):
    """An exception type for attempted (but blocked) page entry overwrites."""

    def __init__(
        self,
        path: PagePathLike
    ) -> None:
        super().__init__(f'Invalid attempt to overwrite page at {str(path)}')
        self._path = path

    @property
    def path(
        self
    ) -> PagePathLike:
        """The path that generated this error."""
        return self._path


class NoSuchPageError(BasePageError, AlmanacKeyError):
    """An exception type for attempting to access a non-existent page."""

    def __init__(
        self,
        path: PagePathLike
    ) -> None:
        path_str = str(path)
        super().__init__(f'No such page {path_str}')

        self._path = str(path)

    @property
    def path(
        self
    ) -> str:
        """The path that generated this error."""
        return self._path


class OutOfBoundsPageError(BasePageError):
    """An exception type for attempting to reference pages beyond the root directory."""

    def __init__(
        self,
        path: PagePathLike
    ) -> None:
        super().__init__(f'No such page {str(path)}')

        self._path = path

    @property
    def path(
        self
    ) -> PagePathLike:
        """The path that generated this error."""
        return self._path


class PathSyntaxError(BasePageError, PositionalValueError):
    """An exception type for path syntax errors."""

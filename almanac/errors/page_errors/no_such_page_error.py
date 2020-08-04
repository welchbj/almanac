"""An exception type for attempting to access a non-existent page."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base_page_error import BasePageError

if TYPE_CHECKING:
    from ...pages import PagePathLike


class NoSuchPageError(BasePageError, KeyError):
    """An exception type for attempting to access a non-existent page."""

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

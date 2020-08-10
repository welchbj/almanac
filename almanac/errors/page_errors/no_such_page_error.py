from __future__ import annotations

from typing import TYPE_CHECKING

from .base_page_error import BasePageError
from ..generic_errors import AlmanacKeyError

if TYPE_CHECKING:
    from ...pages import PagePathLike


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

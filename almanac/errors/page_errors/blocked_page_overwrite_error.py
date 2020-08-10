from __future__ import annotations

from typing import TYPE_CHECKING

from .base_page_error import BasePageError

if TYPE_CHECKING:
    from ...pages import PagePathLike


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

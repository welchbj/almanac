"""Implementation of the ``PageNavigator`` class."""

from .abstract_page import (
    AbstractPage)
from .page_path import (
    PagePath,
    PagePathLike)


class PageNavigator:
    """Encapsulation of page navigation and history logic."""
    # TODO

    def change_directory(
        self,
        destination: PagePathLike
    ) -> None:
        """TODO."""

    def forward(
        self
    ) -> None:
        """TODO."""

    def back(
        self
    ) -> None:
        """TODO."""

    @property
    def current_page(
        self
    ) -> AbstractPage:
        """The current page within this navigator."""
        # TODO

"""Implementation of the ``AbstractSearchablePageIndex`` class."""

from abc import (
    ABC,
    abstractmethod)
from typing import (
    Dict)

from ..abstract_page import (
    AbstractPage)
from ..page_path import (
    PagePathLike)


class AbstractSearchablePageIndex(ABC):

    """TODO."""

    @staticmethod
    def parse_search_query(
        query: str
    ) -> Dict:
        """Parse a string query into a consumable data format."""
        # TODO: figure out return type
        # TODO: better docstring

    # TODO: other abstract methods

    # TODO: below methods should just be wrappers around other abstractmethods

    @abstractmethod
    def __getitem__(
        self,
        path: PagePathLike
    ) -> AbstractPage:
        """Get a page from the index."""
        # TODO

    @abstractmethod
    def __contains__(
        self,
        path: PagePathLike
    ) -> bool:
        """Return whether a specified :class:`PagePathLike` is in the index."""
        # TODO

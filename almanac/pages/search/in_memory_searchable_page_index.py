"""Implementation of the ``PageIndex`` class."""

from ..page_path import (
    PagePath,
    PagePathLike)


# TODO: I think that search logic should be built into the `PageIndex`...
#       so we will need a default `AbstractSearchablePageIndex` from which
#       different implementations can derive

class InMemorySearchablePageIndex:
    """An index of paths to :class:`AbstractPage` instances.

    Attributes:
        TODO

    """

    # TODO

    def __contains__(
        self,
        path: PagePathLike
    ) -> bool:
        """Whether the specified path is contained within this index."""
        # TODO

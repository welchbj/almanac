"""Implementation of the ``PagePath`` class."""

from __future__ import annotations

from enum import (
    auto,
    Enum)
from typing import (
    Any,
    Tuple,
    Union)


class _PathExplodeState(Enum):
    BEGIN = auto()
    IN_SEGMENT = auto()
    ATE_SLASH = auto()
    ATE_ONE_DOT = auto()
    ATE_TWO_DOTS = auto()


class PagePath:
    """An encapsulation of a path pointing to a page."""

    def __init__(
        self,
        path: str
    ) -> None:
        self._path: str = path

    @staticmethod
    def un_trailing_slashify(
        path: PagePathLike
    ) -> PagePath:
        # TODO
        pass

    @property
    def path(
        self
    ) -> str:
        """The string path wrapped in this instance."""
        return self._path

    @property
    def segments(
        self
    ) -> Tuple[str, ...]:
        """The path segments of this class.

        TODO: example

        """
        # TODO

    def explode(
        self,
        path: PagePathLike
    ) -> PagePath:
        """Expand the specified path, using this instance as the start.

        TODO: explain explosion logic

        """
        pass

    def __contains__(
        self,
        path: PagePathLike
    ) -> bool:
        """Whether the :class:`PathLike` is contained in this instance."""
        # TODO: do we need a strong check than this?
        return str(path) in self._path

    def __eq__(
        self,
        other: Any
    ) -> bool:
        if isinstance(other, PagePathLike.__args__):
            return self._path == str(other)

        return False

    def __hash__(
        self
    ) -> int:
        return hash(self._path)


PagePathLike = Union[str, PagePath]

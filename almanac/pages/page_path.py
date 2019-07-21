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
        path: PagePathLike
    ) -> None:
        # TODO: ensure that this path is absolute and only contains valid
        #       path characters
        self._path: str = self.__class__.un_trailing_slashify(str(path))
        self._segments: Tuple[str, ...] = self._path.split('/')

    @staticmethod
    def is_absolute_path(
        path: PagePathLike
    ) -> bool:
        """Whether the specified path is absolute or not (i.e., relative)."""
        return str(path).startswith('/')

    @staticmethod
    def contains_only_valid_chars(
        path: str
    ) -> bool:
        # TODO
        raise NotImplementedError

    @staticmethod
    def un_trailing_slashify(
        path: PagePathLike
    ) -> str:
        path_str = str(path)
        if path_str == '/':
            return '/'

        return path_str.rstrip('/')

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
        return self._segments

    def explode(
        self,
        path: str
    ) -> PagePath:
        """Expand the specified path, using this instance as the start."""
        # TODO: I think this actually fits better in PageNavigator
        raise NotImplementedError

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

    def __str__(
        self
    ) -> str:
        return self._path

    def __repr__(
        self
    ) -> str:
        return f'<{self.__class__.__qualname__} [{str(self)}]>'


PagePathLike = Union[str, PagePath]

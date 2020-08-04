"""Implementation of the ``PagePath`` class."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any, Tuple, Union

from ..errors import PathSyntaxError


class PagePath:
    """An encapsulation of an absolute pseudo-filesystem path."""

    def __init__(
        self,
        path: PagePathLike
    ) -> None:
        candidate_path: str = str(path)
        self.__class__.assert_absolute_path(candidate_path)

        self._segments: Tuple[str, ...] = PurePosixPath(candidate_path).parts
        self._path: str = '/' + '/'.join(self._segments[1:])
        self._parent_dirs = tuple(
            '/' + '/'.join(self._segments[1:i]) for i in
            range(1, len(self._segments))
        )

    @staticmethod
    def assert_absolute_path(
        path: PagePathLike
    ) -> None:
        """Assert that the specified path is absolut.

        Raises:
            PathSyntaxError: If the path is not absolute.

        """
        if not str(path).startswith('/'):
            raise PathSyntaxError('Not an absolute path', 0)

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

        .. code-block:: python

            >>> from almanac import PagePath
            >>> PagePath('/a/b/c').segments
            ('/', 'a', 'b', 'c')
            >>> PagePath('/').segments
            ('/',)

        """
        return self._segments

    @property
    def parent_dirs(
        self
    ) -> Tuple[str, ...]:
        """All parent directory paths of this path.

        .. code-block:: python

            >>> from almanac import PagePath
            >>> print('\\n'.join(PagePath('/a/b/c/d/e').parent_dirs))
            /
            /a
            /a/b
            /a/b/c
            /a/b/c/d

        """
        return self._parent_dirs

    def __contains__(
        self,
        path: PagePathLike
    ) -> bool:
        """Whether the :class:`PathLike` is contained in this instance."""
        return str(path) in self._path

    def __eq__(
        self,
        other: Any
    ) -> bool:
        if isinstance(other, (str, PagePath,)):
            return self._path == str(other)

        return NotImplemented

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

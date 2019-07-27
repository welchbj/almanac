"""Implementation of the ``PagePath`` class."""

from __future__ import annotations

import string

from enum import (
    auto,
    Enum)
from typing import (
    Any,
    Tuple,
    Union)

from ..errors import (
    PositionalValueError)


VALID_PATH_CHARS: str = (
    string.ascii_letters +
    string.digits +
    '-_/')


class _CollapseSlashState(Enum):
    BEGIN = auto()
    IN_SEGMENT = auto()
    IN_SLASHES = auto()


class PagePath:
    """An encapsulation of a path pointing to a page."""

    def __init__(
        self,
        path: PagePathLike
    ) -> None:
        candidate_path: str = str(path)
        self.__class__.assert_absolute_path(candidate_path)
        self.__class__.assert_only_valid_chars(candidate_path)

        candidate_path = self.__class__.collapse_slashes(candidate_path)
        candidate_path = self.__class__.un_trailing_slashify(candidate_path)

        self._path: str = candidate_path
        self._segments: Tuple[str, ...]
        self._parent_dirs: Tuple[str, ...]

        if self._path == '/':
            self._segments = tuple()
            self._parent_dirs = tuple()
        else:
            self._segments = tuple(self._path.split('/')[1:])
            self._parent_dirs = tuple(
                '/' + '/'.join(self._segments[:i]) for i in
                range(len(self._segments)))

    @staticmethod
    def assert_absolute_path(
        path: PagePathLike
    ) -> None:
        """Assert that the specified path is absolut.

        Raises:
            PositionalValueError: If the path is not absolute.

        """
        if not str(path).startswith('/'):
            raise PositionalValueError('Not an absolute path', 0)

    @staticmethod
    def assert_only_valid_chars(
        path: PagePathLike
    ) -> None:
        """Assert that the specified path contains only allowable characters.

        Valid characters include the following:

            * Letters
            * Numbers
            * Dashes (``-``)
            * Underscores (``_``)
            * Forward slashes (``/``), which act as path delimiters

        Raises:
            PositionalValueError: If any invalid characters are encountered.

        """
        for i, c in enumerate(str(path)):
            if c not in VALID_PATH_CHARS:
                raise PositionalValueError('Invalid path character', i)

    @staticmethod
    def collapse_slashes(
        path: str
    ) -> str:
        """Collapse consecutive slashes into single slashes.

        .. code-block:: python

            >>> from almanac import PagePath
            >>> PagePath.collapse_slashes('/my///awesome////path')
            '/my/awesome/path'

        """
        collapsed_path: str = ''
        state: _CollapseSlashState = _CollapseSlashState.BEGIN

        for c in path:
            if state == _CollapseSlashState.BEGIN:
                if c == '/':
                    state = _CollapseSlashState.IN_SLASHES
                else:
                    state = _CollapseSlashState.IN_SEGMENT
            elif state == _CollapseSlashState.IN_SEGMENT:
                if c == '/':
                    state = _CollapseSlashState.IN_SLASHES
                else:
                    collapsed_path += c
            elif state == _CollapseSlashState.IN_SLASHES:
                if c == '/':
                    pass
                else:
                    collapsed_path += '/'
                    collapsed_path += c
                    state = _CollapseSlashState.IN_SEGMENT
            else:
                # this should never happen!
                raise ValueError('Invalid state in collapse_slashes()')

        if state == _CollapseSlashState.IN_SLASHES:
            collapsed_path += '/'

        return collapsed_path

    @staticmethod
    def un_trailing_slashify(
        path: PagePathLike
    ) -> str:
        """Remove the trailing slash from a path.

        .. code-block:: python

            >>> from almanac import PagePath
            >>> PagePath.un_trailing_slashify('/')
            '/'
            >>> PagePath.un_trailing_slashify('/a/b/c/')
            '/a/b/c'

        """
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

        .. code-block:: python

            >>> from almanac import PagePath
            >>> PagePath('/a/b/c').segments
            ('a', 'b', 'c')
            >>> PagePath('/').segments
            ()

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

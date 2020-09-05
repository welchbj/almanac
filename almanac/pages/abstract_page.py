from __future__ import annotations

from abc import ABC, abstractmethod, abstractproperty
from typing import Any, Optional, Set

from .page_path import PagePath, PagePathLike


class AbstractPage(ABC):
    """The base abstract page interface."""

    def __init__(
        self,
        path: PagePathLike,
    ) -> None:
        self._path = PagePath(path)
        self._parent: Optional[AbstractPage] = None
        self._children: Set[AbstractPage] = set()

    @abstractproperty
    def help_text(
        self
    ) -> str:
        """The help text about this page.

        Think of this as a static explanation about the page type's role within the
        greater application, rather than reflecting the current state of this
        particular page.

        """

    @abstractproperty
    def info_text(
        self
    ) -> str:
        """The info text about this page.

        Think of this as a more dynamic output (in contrast to :meth:`help_text`),
        which reflect the current state of this page.

        """

    @abstractmethod
    def get_prompt(
        self
    ) -> str:
        """Return the prompt text for this page.

        This is what is shown on the application's current line, acting as the
        input prompt.

        """

    @property
    def path(
        self
    ) -> PagePath:
        """This page's path."""
        return self._path

    @property
    def parent(
        self
    ) -> Optional[AbstractPage]:
        """The parent page of this page."""
        return self._parent

    @parent.setter
    def parent(
        self,
        new_parent: AbstractPage
    ) -> None:
        self._parent = new_parent

    @property
    def children(
        self
    ) -> Set[AbstractPage]:
        """The immediate children of this page."""
        return self._children

    def __hash__(
        self
    ) -> int:
        return hash(self._path)

    def __eq__(
        self,
        other: Any
    ) -> bool:
        if not isinstance(other, AbstractPage):
            return NotImplemented

        return self._path == other._path

    def __str__(
        self
    ) -> str:
        return str(self.path)

    def __repr__(
        self
    ) -> str:
        return f'<{self.__class__.__qualname__} [{self.path}]>'

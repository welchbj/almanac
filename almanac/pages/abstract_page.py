"""The ``AbstractPage`` class implementation."""

from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
    abstractproperty)
from typing import (
    List,
    Optional,
    Tuple)

from .page_path import (
    PagePath)
from ..shell import (
    EvaluationContext)


class AbstractPage(ABC):
    """The base page class from which all implementations derive.

    Attributes:
        TODO

    TODO

    """

    def __init__(
        self,
        path: str,
    ) -> None:
        self._path = PagePath(path)
        self._parent: Optional[AbstractPage] = None
        self._children: List[AbstractPage] = []

    @abstractproperty
    def allowed_commands(
        self
    ) -> Tuple[str, ...]:
        """The commands that can be executed on this page."""

    @abstractproperty
    def help_text(
        self
    ) -> str:
        """The help text about this page.

        Think of this as a static explanation about the page type's role
        within the greater application, rather than reflecting the current
        state of this particular page.

        """

    @abstractproperty
    def info_text(
        self
    ) -> str:
        """The info text about this page.

        Think of this as a more dynamic output (in contrast to
        :method:`help_text`), which reflect the current state of this page.

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

    @property
    def children(
        self
    ) -> List[AbstractPage]:
        """The immediate children of this page."""
        return self._children

    def get_base_evaluation_context(
        self
    ) -> EvaluationContext:
        """Get the base ``EvaluationContext`` for this type of page.

        Page implementations can override this method to inject default
        data into the base context in which all commands will be evaluated.
        For example, a certain type of page may want some basic variables
        defined.

        If this is not overriden by the page implementation, then a barebones
        :class:``EvaluationContext`` is returned.

        """
        return EvaluationContext()

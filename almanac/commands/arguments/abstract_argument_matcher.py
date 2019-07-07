"""Implementation of the ``ArgumentMatcher`` class."""

from abc import (
    ABC,
    abstractmethod)

from ...shell import (
    Shlexer)


class AbstractArgumentMatcher(ABC):
    """A class for matching arguments.

    TODO: explanation

    """

    @abstractmethod
    def does_match(
        self,
        shlexer: Shlexer
    ) -> bool:
        """Return whether this instance matchers the ``Shlexer``'s state."""

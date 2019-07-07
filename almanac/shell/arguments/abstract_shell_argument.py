"""Implementation of the ``AbstractShellArgument`` class."""

from abc import (
    ABC,
    abstractmethod)
from typing import (
    Any)

from ..evaluation_context import (
    EvaluationContext)


class AbstractShellArgument(ABC):
    """Base class of all shell argument implementations."""

    def __init__(
        self,
        raw_argument: str
    ) -> None:
        self._raw_argument: str = raw_argument

    @abstractmethod
    def evaluate(
        self,
        evaluation_context: EvaluationContext
    ) -> Any:
        """Fully evaluate this argument in the given context."""

    @property
    def raw_argument(
        self
    ) -> str:
        """The un-evaluated raw form of this argument."""
        return self._raw_argument

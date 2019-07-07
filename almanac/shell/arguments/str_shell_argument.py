"""Implementation of the ``StrShellArgument`` class."""

from .abstract_shell_argument import (
    AbstractShellArgument)
from ..evaluation_context import (
    EvaluationContext)


class StrShellArgument(AbstractShellArgument):
    """An :class:``AbstractShellArgument`` representing a raw string."""

    def evaluate(
        self,
        evaluation_context: EvaluationContext
    ) -> str:
        return self.raw_argument

"""Implementation of the ``InlineCommandShellArgument`` class."""

from .abstract_shell_argument import (
    AbstractShellArgument)
from ..evaluation_context import (
    EvaluationContext)


class InlineCommandShellArgument(AbstractShellArgument):
    """An :class:``AbstractShellArgument`` representing an inline command."""

    def evaluate(
        self,
        evaluation_context: EvaluationContext
    ) -> str:
        # TODO
        raise NotImplementedError

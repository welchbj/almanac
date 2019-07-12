"""Implementation of the ``VariableShellArgument`` class."""

from .abstract_shell_argument import (
    AbstractShellArgument)
from ..evaluation_context import (
    EvaluationContext)


class VariableShellArgument(AbstractShellArgument):
    """An :class:`AbstractShellArgument` representing a shell variable."""

    def evaluate(
        self,
        evaluation_context: EvaluationContext
    ) -> str:
        # TODO
        raise NotImplementedError

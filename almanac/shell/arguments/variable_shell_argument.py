"""Implementation of the ``VariableShellArgument`` class."""

from typing import (
    Any)

from .abstract_shell_argument import (
    AbstractShellArgument)
from ..evaluation_context import (
    EvaluationContext)
from ..shell_tokens import (
    ShellTokens)


class VariableShellArgument(AbstractShellArgument):
    """An :class:`AbstractShellArgument` representing a shell variable."""

    def evaluate(
        self,
        evaluation_context: EvaluationContext
    ) -> Any:
        var_name: str = self.raw_argument
        if var_name.startswith(ShellTokens.VARIABLE_BEGIN_TOKEN):
            var_name = var_name[1:]

        try:
            return evaluation_context.variables[var_name]
        except KeyError as e:
            raise ValueError(f'Unknown variable `{var_name}`') from e

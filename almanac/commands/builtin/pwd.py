"""Implementation of the ``PwdCommand`` class."""

from typing import (
    Iterator,
    Tuple)

from prompt_toolkit.completion import (
    Completion)

from ..abstract_command import (
    AbstractCommand)
from ...shell import (
    AbstractShellArgument,
    EvaluationContext,
    Shlexer)


class PwdCommand(AbstractCommand):
    """Print the current working directory."""

    async def run(
        self,
        evaluation_context: EvaluationContext,
        *args: AbstractShellArgument
    ) -> None:
        # TODO
        raise NotImplementedError

    def get_completions(
        self,
        shlexer: Shlexer
    ) -> Iterator[Completion]:
        # TODO
        raise NotImplementedError

    @property
    def name(
        self
    ) -> str:
        return 'pwd'

    @property
    def aliases(
        self
    ) -> Tuple[str, ...]:
        return ('cwd',)

    @property
    def brief_description(
        self
    ) -> str:
        # TODO
        return 'TODO - PwdCommand brief_description'

    @property
    def detailed_usage(
        self
    ) -> str:
        # TODO
        return 'TODO - PwdCommand detailed_usage'

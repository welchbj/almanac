"""Implementation of the ``CdCommand`` class."""

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


class CdCommand(AbstractCommand):
    """Change the application's current directory."""

    async def run(
        self,
        evaluation_context: EvaluationContext,
        *args: AbstractShellArgument
    ) -> None:
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
        return 'cd'

    @property
    def aliases(
        self
    ) -> Tuple[str, ...]:
        return tuple()

    @property
    def brief_description(
        self
    ) -> str:
        # TODO
        return 'TODO - CdCommand brief_description'

    @property
    def detailed_usage(
        self
    ) -> str:
        # TODO
        return 'TODO - CdCommand detailed_usage'

"""Implementation of the ``BackCommand`` class."""

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


class BackCommand(AbstractCommand):
    """Jump to the last page in the application's history."""

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
        return 'back'

    @property
    def aliases(
        self
    ) -> Tuple[str, ...]:
        return ('b',)

    @property
    def brief_description(
        self
    ) -> str:
        # TODO
        return 'TODO - BackCommand brief_description'

    @property
    def detailed_usage(
        self
    ) -> str:
        # TODO
        return 'TODO - BackCommand detailed_usage'

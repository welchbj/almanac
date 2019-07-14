"""Implementation of the ``SearchCommand`` class."""

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


class SearchCommand(AbstractCommand):
    """Search through the application's pages."""

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
        return 'search'

    @property
    def aliases(
        self
    ) -> Tuple[str, ...]:
        return ('s',)

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

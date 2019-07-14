"""Implementation of the ``ForwardCommand`` class."""

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


class ForwardCommand(AbstractCommand):
    """Jump forward in the application's navigation history."""

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
        return 'forward'

    @property
    def aliases(
        self
    ) -> Tuple[str, ...]:
        return ('f',)

    @property
    def brief_description(
        self
    ) -> str:
        # TODO
        return 'TODO - ForwardCommand brief_description'

    @property
    def detailed_usage(
        self
    ) -> str:
        # TODO
        return 'TODO - ForwardCommand detailed_usage'

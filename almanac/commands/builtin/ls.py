"""Implementation of the ``LsCommand`` class."""

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


class LsCommand(AbstractCommand):
    """List the contents of the current directory."""

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
        return 'ls'

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
        return 'TODO - LsCommand brief_description'

    @property
    def detailed_usage(
        self
    ) -> str:
        # TODO
        return 'TODO - LsCommand detailed_usage'

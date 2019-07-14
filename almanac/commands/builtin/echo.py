"""Implementation of the ``EchoCommand`` class."""

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


class EchoCommand(AbstractCommand):
    """Echo a string to stdout."""

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
        return 'echo'

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
        return 'TODO - EchoCommand brief_description'

    @property
    def detailed_usage(
        self
    ) -> str:
        # TODO
        return 'TODO - EchoCommand detailed_usage'

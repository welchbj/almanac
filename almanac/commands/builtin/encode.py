"""Implementation of the ``EncodeCommand`` class."""

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


class EncodeCommand(AbstractCommand):
    """Encode a string using a codec like ``base64``."""

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
        return 'encode'

    @property
    def aliases(
        self
    ) -> Tuple[str, ...]:
        return ('enc',)

    @property
    def brief_description(
        self
    ) -> str:
        # TODO
        return 'TODO - EncodeCommand brief_description'

    @property
    def detailed_usage(
        self
    ) -> str:
        # TODO
        return 'TODO - EncodeCommand detailed_usage'

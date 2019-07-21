"""Implementation of the ``AbstractCommand`` class."""

from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
    abstractproperty)
from itertools import (
    chain)
from typing import (
    Iterator,
    Tuple)

from prompt_toolkit.completion import (
    Completion)

from ..shell import (
    AbstractShellArgument,
    EvaluationContext,
    Shlexer)


class AbstractCommand(ABC):
    """The base class from which all commands are derived.

    Attributes:
        TODO

    TODO

    """

    @abstractmethod
    def get_completions(
        self,
        shlexer: Shlexer
    ) -> Iterator[Completion]:
        """Get the command's completions for the specified ``Shlexer``."""

    @abstractmethod
    async def run(
        self,
        evaluation_context: EvaluationContext,
        *args: AbstractShellArgument
    ) -> None:
        """Run the command.

        TODO: explanation of how it all works
        TODO: explanation of expansion of shell arguments

        Args:
            args: The arguments to be parsed and used in command execution.

        """

    @abstractproperty
    def name(
        self
    ) -> str:
        """The name of this command.

        This will be the main string used to invoke this command from the
        command-line.

        """

    @abstractproperty
    def aliases(
        self
    ) -> Tuple[str, ...]:
        """Aliases for this command, which can be used to invoke it."""

    @abstractproperty
    def brief_description(
        self
    ) -> str:
        """A short, one-sentence description of what this command does."""

    @abstractproperty
    def detailed_usage(
        self
    ) -> str:
        """The in-depth explanation (the "man page") for this command."""

    @property
    def identifiers(
        self
    ) -> Tuple[str, ...]:
        """A tuple contain the `name` and all `aliases` of this command."""
        return tuple(chain((self.name,), self.aliases))

    def __eq__(
        self,
        other: AbstractCommand
    ) -> bool:
        return self.name == other.name

    # TODO: __str__ / __repr__

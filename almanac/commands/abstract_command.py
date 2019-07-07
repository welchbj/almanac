"""Implementation of the ``AbstractCommand`` class."""

from abc import (
    ABC,
    abstractmethod,
    abstractproperty)
from typing import (
    Iterator,
    Tuple,
    TYPE_CHECKING)

from prompt_toolkit.completion import (
    Completion)

from .arguments import (
    AbstractArgumentMatcher)
from ..shell import (
    AbstractShellArgument,
    EvaluationContext,
    Shlexer)

if TYPE_CHECKING:
    from ..app import (
        Application)


class AbstractCommand(ABC):
    """The base class from which all commands are derived.

    Attributes:
        TODO

    TODO

    """

    def __init__(
        self,
        app: 'Application'
    ) -> None:
        self._app = app
        # TODO

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
    def argument_matchers(
        self
    ) -> Tuple[AbstractArgumentMatcher, ...]:
        """Matchers for any arguments supported by this command.

        TODO: description of what this actually does

        """

    def get_completions(
        self,
        shlexer: Shlexer
    ) -> Iterator[Completion]:
        """Get the command's completions for the specified ``Shlexer``."""
        # TODO: think about how this fits in with the big picture
        # TODO: can this just be derived from however we end up describing
        #       the arguments for a given command?

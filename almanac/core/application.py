"""Implementation of the ``Application`` class."""

import shlex

from contextlib import (
    contextmanager)
from typing import (
    ContextManager,
    List,
    Union)

from docopt import (
    docopt,
    DocoptExit)
from prompt_toolkit import (
    PromptSession)
from prompt_toolkit.patch_stdout import (
    patch_stdout)

from ..commands import (
    Command,
    CommandCallable,
    CommandEngine)
from ..pages import (
    PageNavigator)
from ..io import (
    AbstractIoContext,
    StandardConsoleIoContext)


class Application:
    """The core class of ``almanac``, wrapping everything together.

    Attributes:
        TODO

    TODO: examples

    """

    def __init__(
        self
    ) -> None:
        # TODO: load some configuration options and put them into the session

        self._io_stack: List[AbstractIoContext] = [
            StandardConsoleIoContext()
        ]

        self._command_engine = CommandEngine()
        self._page_navigator = PageNavigator()
        self._session = PromptSession(
            message=self._prompt_callback,
            # completer=TODO
            complete_while_typing=True,
            complete_in_thread=True)

    @property
    def page_navigator(
        self
    ) -> PageNavigator:
        """The :class:`PageNavigator` powering this app's navigation."""
        return self._page_navigator

    @property
    def command_engine(
        self
    ) -> CommandEngine:
        """The :class:`CommandEngine` powering this app's command lookup."""
        return self._command_engine

    @property
    def io(
        self
    ) -> AbstractIoContext:
        """The application's top-level input/output context."""
        return self._io_stack[-1]

    @contextmanager
    def io_context(
        self,
        new_io_context: AbstractIoContext
    ) -> ContextManager[AbstractIoContext]:
        """Change the app's current input/output context."""
        self._io_stack.append(new_io_context)
        yield new_io_context
        self._io_stack.pop()

    async def eval_line(
        self,
        line: str
    ) -> int:
        """Evaluate a line passed to the application by the user."""
        args = shlex.split(line)
        if not args:
            return 0

        name_or_alias = args[0]
        try:
            command = self._command_engine[name_or_alias]
            opts = docopt(command.doc, argv=args[1:])
            command(self, self.io, opts)
        except KeyError:
            self.print_command_suggestions(name_or_alias)
            return 1
        except DocoptExit as e:
            self.io.print_err(f'Invalid arguments for command {command.name}')
            self.io.print_raw(e)
            return 1
        except SystemExit:
            # raised by docopt for -h/--help
            pass

        return 0

    async def run(
        self
    ) -> int:
        """Run the application's event loop.

        Returns:
            The exit code of the application's execution.

        """
        with patch_stdout():
            while True:
                try:
                    line = (await self._session.prompt_async()).strip()
                    if not line:
                        continue

                    await self.eval_line(line)
                except KeyboardInterrupt:
                    continue
                except EOFError:
                    break
                finally:
                    # TODO: this needs to clean up running tasks
                    pass

            return 0

    def command(
        self,
        new_command: Union[Command, CommandCallable]
    ) -> Command:
        """Register a command on this application.

        TODO

        Args:
            new_command: Either a :class:`Command` instance or a
                :class:`CommandCallable` function. This will be registered
                on this class's :data:`command_engine` attribute.

        Returns:
            The created :class:`Command` instance.

        Raises:
            CommandNameCollisionError: If an attempt is made to register a
                command with a name or alias(es) that conflict with already-
                registered commands.

        """
        if not isinstance(new_command, Command):
            new_command = Command.from_callable(new_command)

        self._command_engine.register_command(new_command)
        return new_command

    def print_command_suggestions(
        self,
        name_or_alias: str
    ) -> None:
        """Print command recommendations for a misspelled attempt.

        It is assumed that lookup has already been attempted and that no
        matching command exists.

        """
        # TODO
        print('print_command_suggestions not yet implemented!')

    def _prompt_callback(
        self
    ) -> str:
        """A callback for getting the current page's prompt."""
        return self._page_navigator.current_page.get_prompt()

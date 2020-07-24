"""Implementation of the ``Application`` class."""

import asyncio
import sys

import pyparsing as pp

from contextlib import contextmanager
from typing import (
    Any,
    Awaitable,
    Callable,
    Iterator,
    List,
    NoReturn,
    Union
)

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

from .context import set_current_app
from ..commands import (
    Command,
    CommandCompleter,
    CommandCoroutine,
    CommandEngine,
    parse_cmd_line
)
from ..constants import ExitCodes
from ..errors import (
    CommandArgumentError,
    CommandPartialParseError,
    CommandRegistrationError,
    CommandTotalParseError,
    NoSuchCommandError
)
from ..io import AbstractIoContext, StandardConsoleIoContext
from ..pages import PageNavigator


class Application:
    """The core class of ``almanac``, wrapping everything together."""

    def __init__(
        self
    ) -> None:
        self._io_stack: List[AbstractIoContext] = [
            StandardConsoleIoContext()
        ]

        self._command_engine = CommandEngine()
        self._page_navigator = PageNavigator()
        self._session = PromptSession(
            message=self._prompt_callback,
            completer=CommandCompleter(self),
            complete_while_typing=True,
            complete_in_thread=True
        )

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
    ) -> Iterator[AbstractIoContext]:
        """Change the app's current input/output context."""
        self._io_stack.append(new_io_context)
        yield new_io_context
        self._io_stack.pop()

    async def eval_line(
        self,
        line: str
    ) -> int:
        """Evaluate a line passed to the application by the user."""
        try:
            parsed_args: pp.ParseResults = parse_cmd_line(line)
        except CommandPartialParseError as e:
            self.io.print_err(
                'Error in command parsing. Suspected error position marked below:'
            )
            self.io.print_err(line)
            self.io.print_err(' ' * e.error_pos + '^')

            return ExitCodes.ERR_COMMAND_PARSING
        except CommandTotalParseError:
            self.io.print_err('Error in command parsing.')
            return ExitCodes.ERR_COMMAND_PARSING

        if not parsed_args:
            return ExitCodes.OK

        name_or_alias = parsed_args.command
        try:
            return await self.call_as_current_app(
                self._command_engine.run, name_or_alias, parsed_args
            )
        except CommandArgumentError as e:
            self.io.print_err(e)

            # TODO
            print(e.argument_state)

            return ExitCodes.ERR_COMMAND_INVALID_ARGUMENTS
        except NoSuchCommandError:
            self.io.print_err(f'Command {name_or_alias} does not exist')
            self._print_command_suggestions(name_or_alias)
            return ExitCodes.ERR_COMMAND_NONEXISTENT

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

            return ExitCodes.OK

    async def call_as_current_app(
        self,
        coro: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Helper for calling a coroutine with the current app set to this instance."""
        set_current_app(self)
        return await coro(*args, **kwargs)

    def quit(
        self,
        exit_code: int
    ) -> NoReturn:
        # TODO: this should really not be sys.exit-ing... just need the app to stop
        sys.exit(exit_code)

    def command(
        self,
        new_command: Union[Command, CommandCoroutine]
    ) -> Command:
        """Register a command on this application.

        Args:
            new_command: Either a :class:`Command` instance or a
                :class:`CommandCoroutine` function. This will be registered
                on this class's :data:`command_engine` attribute.

        Returns:
            The created :class:`Command` instance.

        Raises:
            CommandNameCollisionError: If an attempt is made to register a
                command with a name or alias(es) that conflict with already-
                registered commands.

        """
        if not isinstance(new_command, Command):
            if not asyncio.iscoroutinefunction(new_command):
                raise CommandRegistrationError(
                    'Attempted to register a command with non-async '
                    f'function {new_command.__name__}'
                )

            new_command = Command(new_command)

        self._command_engine.register(new_command)
        return new_command

    def _print_command_suggestions(
        self,
        name_or_alias: str
    ) -> None:
        """Print command recommendations for a misspelled attempt.

        It is assumed that lookup has already been attempted and that no
        matching command exists.

        """
        suggestions = self._command_engine.get_suggestions(name_or_alias)
        if not suggestions:
            return

        self.io.print_info('Perhaps you meant one of these:')
        for suggestion in suggestions:
            self.io.print_raw('    ', suggestion, sep='')

    def _prompt_callback(
        self
    ) -> str:
        """A callback for getting the current page's prompt."""
        return self._page_navigator.current_page.get_prompt()

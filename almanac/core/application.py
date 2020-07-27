"""Implementation of the ``Application`` class."""

from contextlib import contextmanager
from typing import (
    Any,
    Awaitable,
    Callable,
    Iterable,
    Iterator,
    List,
    Optional,
    TypeVar,
    Union
)

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

from .command_completer import CommandCompleter
from .command_engine import CommandEngine
from .context import set_current_app
from .decorators import CommandDecorator
from .decorators import (
    argument as argument_decorator,
    completer as completer_decorator,
    description as description_decorator,
    name as name_decorator
)
from ..commands import FrozenCommand, MutableCommand
from ..constants import ExitCodes
from ..errors import BaseArgumentError, NoSuchCommandError
from ..io import AbstractIoContext, StandardConsoleIoContext
from ..pages import PageNavigator
from ..parsing import parse_cmd_line, ParseState
from ..types import CommandCoroutine

_T = TypeVar('_T')


class Application:
    """The core class of ``almanac``, wrapping everything together."""

    def __init__(
        self
    ) -> None:
        self._io_stack: List[AbstractIoContext] = [
            StandardConsoleIoContext()
        ]

        self._is_running = False
        self._do_quit = False

        self._command_engine = CommandEngine()
        self._page_navigator = PageNavigator()
        self._session = PromptSession(
            message=self._prompt_callback,
            completer=CommandCompleter(self),
            complete_while_typing=True,
            complete_in_thread=True
        )

    @property
    def is_running(
        self
    ) -> bool:
        """"Whether this application is currently runnnig."""
        return self._is_running

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
        parse_status = parse_cmd_line(line)

        if parse_status.state == ParseState.PARTIAL:
            self.io.print_err(
                'Error in command parsing. Suspected error position marked below:'
            )
            self.io.print_err(line)
            self.io.print_err(' ' * parse_status.unparsed_start_pos + '^')

            return ExitCodes.ERR_COMMAND_PARSING
        elif parse_status.state == ParseState.NONE:
            self.io.print_err('Error in command parsing.')
            return ExitCodes.ERR_COMMAND_PARSING

        parsed_args = parse_status.results
        if not parsed_args:
            return ExitCodes.OK

        name_or_alias = parsed_args.command
        try:
            return await self.call_as_current_app_async(
                self._command_engine.run, name_or_alias, parsed_args
            )
        except BaseArgumentError as e:
            self.io.print_err(e)

            # TODO

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
        self._is_running = True

        with patch_stdout():
            while True:
                try:
                    if self._do_quit:
                        break

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
                    self._is_running = False

            return ExitCodes.OK

    def call_as_current_app(
        self,
        func: Callable[..., _T],
        *args: Any,
        **kwargs: Any,
    ) -> _T:
        """Call a synchronous function with the current app set to this instance."""
        set_current_app(self)
        return func(*args, **kwargs)

    async def call_as_current_app_async(
        self,
        coro: Callable[..., Awaitable[_T]],
        *args: Any,
        **kwargs: Any,
    ) -> _T:
        """Call a coroutine with the current app set to this instance."""
        set_current_app(self)
        return await coro(*args, **kwargs)

    def quit(
        self
    ) -> None:
        """Cause this application to cleanly stop running."""
        self._do_quit = True

    def command(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        aliases: Optional[Union[str, Iterable[str]]] = None
    ) -> CommandDecorator:
        """A decorator for registering a command on this application.

        This should always be the top-most (i.e., lowest line number) decorator in a
        stack on top of your command's coroutine.

        """

        def wrapped(
            new_command: Union[MutableCommand, CommandCoroutine]
        ) -> FrozenCommand:
            new_command = MutableCommand.ensure_command(new_command)

            if name is not None:
                new_command.name = name

            if description is not None:
                new_command.description = description

            if aliases is not None:
                new_command.add_alias(*aliases)

            frozen_command = new_command.freeze()
            self._command_engine.register(frozen_command)
            return frozen_command

        return wrapped

    def cmd_aliases(
        self,
        *alias_names: str
    ) -> CommandDecorator:
        """Shorthand decorator for specifying a command's alias(es)."""

        def wrapped(
            new_command: Union[MutableCommand, CommandCoroutine]
        ) -> MutableCommand:
            new_command = MutableCommand.ensure_command(new_command)
            new_command.add_alias(*alias_names)
            return new_command

        return wrapped

    def cmd_description(
        self,
        description: str
    ) -> CommandDecorator:
        """Shorthand decorator for specifying a command's description."""

        def wrapped(
            new_command: Union[MutableCommand, CommandCoroutine]
        ) -> MutableCommand:
            new_command = MutableCommand.ensure_command(new_command)
            new_command.description = description
            return new_command

        return wrapped

    def cmd_name(
        self,
        name: str
    ) -> CommandDecorator:
        """Shorthand decorator for specifying a command's name."""

        def wrapped(
            new_command: Union[MutableCommand, CommandCoroutine]
        ) -> MutableCommand:
            new_command = MutableCommand.ensure_command(new_command)
            new_command.name = name
            return new_command

        return wrapped

    # Argument-modification decorators are stored on this class as a convenience.
    arg = staticmethod(argument_decorator)
    arg_completer = staticmethod(completer_decorator)
    arg_description = staticmethod(description_decorator)
    arg_name = staticmethod(name_decorator)

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

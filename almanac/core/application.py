"""Implementation of the ``Application`` class."""

import asyncio

from contextlib import contextmanager
from typing import Any, Awaitable, Callable, Dict, Iterator, List, Type, TypeVar

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style

from .command_completer import CommandCompleter
from .command_engine import CommandEngine
from .decorators import ArgumentDecoratorProxy, CommandDecoratorProxy, CoroutineCallback
from ..constants import ExitCodes
from ..context import set_current_app
from ..errors import (
    BaseArgumentError,
    ConflictingPromoterTypesError,
    NoSuchCommandError
)
from ..io import AbstractIoContext, StandardConsoleIoContext
from ..pages import PageNavigator
from ..parsing import get_lexer_cls_for_app, parse_cmd_line, ParseState
from ..style import DARK_MODE_STYLE

_T = TypeVar('_T')


class Application:
    """The core class of ``almanac``, wrapping everything together."""

    def __init__(
        self,
        *,
        with_completion: bool = True,
        with_style: bool = True,
        style: Style = DARK_MODE_STYLE,
        io_context_cls: Type[AbstractIoContext] = StandardConsoleIoContext,
        propagate_runtime_exceptions: bool = False
    ) -> None:
        self._io_stack: List[AbstractIoContext] = [io_context_cls()]

        self._do_quit = False

        self._propagate_runtime_exceptions = propagate_runtime_exceptions

        self._on_exit_callbacks: List[CoroutineCallback] = []
        self._on_init_callbacks: List[CoroutineCallback] = []

        self._command_engine = CommandEngine()
        self._page_navigator = PageNavigator()

        self._type_completer_mapping: Dict[Type, List[Completer]] = {}

        self._command_decorator_proxy = CommandDecoratorProxy(self)
        self._argument_decorator_proxy = ArgumentDecoratorProxy()

        self._session_opts: Dict[str, Any] = {}
        self._session_opts['message'] = self._prompt_callback

        if with_completion:
            self._session_opts['completer'] = CommandCompleter(self)
            self._session_opts['complete_while_typing'] = True
            self._session_opts['complete_in_thread'] = True

        if with_style:
            lexer_cls = get_lexer_cls_for_app(self)
            self._session_opts['lexer'] = PygmentsLexer(lexer_cls)
            self._session_opts['style'] = style

    @property
    def cmd(
        self
    ) -> CommandDecoratorProxy:
        """The interface for command-mutating decorators."""
        return self._command_decorator_proxy

    @property
    def arg(
        self
    ) -> ArgumentDecoratorProxy:
        """The interface for argument-mutating decorators."""
        return self._argument_decorator_proxy

    @property
    def on_exit_callbacks(
        self
    ) -> List[CoroutineCallback]:
        """Registered coroutines to be executed on application exit."""
        return self._on_exit_callbacks

    @property
    def on_init_callbacks(
        self
    ) -> List[CoroutineCallback]:
        """Registered coroutines to be executed on application prompt initialization."""
        return self._on_init_callbacks

    @property
    def type_completer_mapping(
        self
    ) -> Dict[Type, List[Completer]]:
        """A mapping of types to registered global completers."""
        return self._type_completer_mapping

    @property
    def type_promoter_mapping(
        self
    ) -> Dict[Type, Callable]:
        """A mapping of types to callables that convert raw arguments to those types."""
        return self._command_engine.type_promoter_mapping

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
            # TODO: handle the finer grained argument exeception types

            self._maybe_propagate_runtime_exc(e)
            return ExitCodes.ERR_COMMAND_INVALID_ARGUMENTS
        except NoSuchCommandError as e:
            self.io.print_err(f'Command {name_or_alias} does not exist')
            self._print_command_suggestions(name_or_alias)

            self._maybe_propagate_runtime_exc(e)
            return ExitCodes.ERR_COMMAND_NONEXISTENT

    async def prompt(
        self
    ) -> int:
        """Run the application's interactive prompt.

        This method will fire all registered on-init callbacks when it first begins,
        and fire all registered on-exit callbacks when it completes execution.

        Returns:
            The exit code of the application's execution.

        """
        with patch_stdout():
            await self.run_on_init_callbacks()

            session = PromptSession(**self._session_opts)

            while True:
                try:
                    if self._do_quit:
                        break

                    line = (await session.prompt_async()).strip()
                    if not line:
                        continue

                    await self.eval_line(line)
                except KeyboardInterrupt:
                    continue
                except EOFError:
                    break
                finally:
                    await self.run_on_exit_callbacks()

            return ExitCodes.OK

    def add_completers_for_type(
        self,
        _type: Type,
        *completers: Completer
    ) -> None:
        """Register a completer for all arguments of a specified type (globally)."""
        if _type not in self._type_completer_mapping.keys():
            self._type_completer_mapping[_type] = []

        for completer in completers:
            self._type_completer_mapping[_type].append(completer)

    def add_promoter_for_type(
        self,
        _type: Type,
        promoter_callable: Callable
    ) -> None:
        """Register a promotion callable for a specific argument type."""
        try:
            self._command_engine.add_promoter_for_type(_type, promoter_callable)
        except ConflictingPromoterTypesError as e:
            raise e

    def promoter_for(
        self,
        *types: Type[_T]
    ) -> Callable[[Any], Callable[[Any], _T]]:
        """A decorator for specifying inline promotion callbacks."""

        def decorator(
            f: Callable[[Any], _T]
        ) -> Callable[[Any], _T]:
            for _type in types:
                self.add_promoter_for_type(_type, f)
            return f

        return decorator

    def on_exit(
        self
    ) -> Callable[[CoroutineCallback], CoroutineCallback]:
        """A decorator for specifying a callback to be executed when the app exits.

        These callbacks will only be implicitly executed at the end of :method:`prompt`
        execution. Otherwise, the programmer must manually call
        :method:`run_on_init_callbacks`.

        """

        def decorator(
            callback_coro: CoroutineCallback
        ) -> CoroutineCallback:
            self._on_exit_callbacks.append(callback_coro)
            return callback_coro

        return decorator

    def on_init(
        self
    ) -> Callable[[CoroutineCallback], CoroutineCallback]:
        """A decorator for specifying a callback to be executed when the prompt begins.

        These callbacks will only be implicitly executed at the beginning of
        :method:`prompt` execution. Otherwise, the programmer must manually call
        :method:`run_on_init_callbacks`.

        """

        def decorator(
            callback_coro: CoroutineCallback
        ) -> CoroutineCallback:
            self._on_init_callbacks.append(callback_coro)
            return callback_coro

        return decorator

    async def run_on_exit_callbacks(
        self
    ) -> List[Any]:
        """Run all of the registered on-exit callbacks.

        Returns:
            The return value of each of the registered callbacks, in the order that
            they were registered.

        """
        awaitable_callbacks = [x() for x in self._on_exit_callbacks]
        return await asyncio.gather(*awaitable_callbacks)

    async def run_on_init_callbacks(
        self
    ) -> List[Any]:
        """Run all of the registered on-init callbacks.

        Returns:
            The return value of each of the registered callbacks, in the order that
            they were registered.

        """
        awaitable_callbacks = [x() for x in self._on_init_callbacks]
        return await asyncio.gather(*awaitable_callbacks)

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

    def _maybe_propagate_runtime_exc(
        self,
        exc: Exception
    ) -> None:
        if self._propagate_runtime_exceptions:
            raise exc

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

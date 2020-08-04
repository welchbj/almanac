"""Implementation of the ``Application`` class."""

import asyncio
import traceback

from contextlib import contextmanager
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Type,
    TypeVar
)

from munch import Munch
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers.python import Python3TracebackLexer

from .command_completer import CommandCompleter
from .command_engine import CommandEngine
from .decorators import ArgumentDecoratorProxy, CommandDecoratorProxy
from ..constants import ExitCodes
from ..context import set_current_app
from ..errors import ConflictingPromoterTypesError, InvalidCallbackTypeError
from ..hooks import (
    AsyncNoArgsCallback,
    assert_async_callback,
    assert_sync_callback,
    HookProxy,
    PromoterFunction,
    SyncNoArgsCallback
)
from ..io import AbstractIoContext, StandardConsoleIoContext
from ..pages import PageNavigator, PagePath
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
        propagate_runtime_exceptions: bool = False,
        print_all_exception_tracebacks: bool = False,
        print_unknown_exception_tracebacks: bool = True
    ) -> None:
        self._io_stack: List[AbstractIoContext] = [io_context_cls()]

        self._do_quit = False

        self._propagate_runtime_exceptions = propagate_runtime_exceptions
        self._print_all_exception_tracebacks = print_all_exception_tracebacks
        self._print_unknown_exception_tracebacks = print_unknown_exception_tracebacks

        self._on_exit_callbacks: List[AsyncNoArgsCallback[Any]] = []
        self._on_init_callbacks: List[AsyncNoArgsCallback[Any]] = []

        self._bag = Munch()
        self._command_engine = CommandEngine(self)
        self._page_navigator = PageNavigator()

        self._type_completer_mapping: Dict[Type, List[Completer]] = {}

        self._command_decorator_proxy = CommandDecoratorProxy(self)
        self._argument_decorator_proxy = ArgumentDecoratorProxy()
        self._hook_proxy = HookProxy(self)

        self._prompt_callback: SyncNoArgsCallback[str] = self._default_prompt_callback

        self._session_opts: Dict[str, Any] = {}
        self._session_opts['message'] = self._prompt_callback_wrapper

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
    def hook(
        self
    ) -> HookProxy:
        """The top-level interface for registering hooks on different events."""
        return self._hook_proxy

    @property
    def bag(
        self
    ) -> Munch:
        """A mutable container for storing data for global access."""
        return self._bag

    @property
    def current_prompt_str(
        self
    ) -> str:
        """The current prompt string."""
        return self._prompt_callback_wrapper()

    @property
    def current_path(
        self
    ) -> PagePath:
        """Shorthand for a getting the application's current path."""
        return self._page_navigator.current_page.path

    @property
    def on_exit_callbacks(
        self
    ) -> List[AsyncNoArgsCallback[Any]]:
        """Registered coroutines to be executed on application exit."""
        return self._on_exit_callbacks

    @property
    def on_init_callbacks(
        self
    ) -> List[AsyncNoArgsCallback[Any]]:
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
    ) -> Dict[Type[_T], PromoterFunction[_T]]:
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
            self.io.error(
                'Error in command parsing. Suspected error position marked below:'
            )
            self.io.error(line)
            self.io.error(' ' * parse_status.unparsed_start_pos + '^')

            return ExitCodes.ERR_COMMAND_PARSING
        elif parse_status.state == ParseState.NONE:
            self.io.error('Error in command parsing.')
            return ExitCodes.ERR_COMMAND_PARSING

        parsed_args = parse_status.results
        if not parsed_args:
            return ExitCodes.OK

        name_or_alias = parsed_args.command
        try:
            return await self.call_as_current_app_async(
                self._command_engine.run, name_or_alias, parsed_args
            )
        except Exception as e:
            exc_hook_table = self._hook_proxy.exception
            exc_hook_coro = exc_hook_table.get_hook_for_exc_type(type(e))

            if exc_hook_coro is None:
                self.print_exception_info(e, unknown=True)
            else:
                await self.call_as_current_app_async(exc_hook_coro, e)

            self._maybe_propagate_runtime_exc(e)
            return ExitCodes.ERR_RUNTIME_EXC

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
            try:
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
                        # KeyboardInterrupt is a special exception case, since it is not
                        # a descendant of the Exception base class.
                        continue
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
        _type: Type[_T],
        promoter_callable: PromoterFunction[_T]
    ) -> None:
        """Register a promotion callable for a specific argument type."""
        try:
            self._command_engine.add_promoter_for_type(_type, promoter_callable)
        except ConflictingPromoterTypesError as e:
            raise e

    def promoter_for(
        self,
        *types: Type[_T]
    ) -> Callable[[PromoterFunction[_T]], PromoterFunction[_T]]:
        """A decorator for specifying inline promotion callbacks."""

        def decorator(
            f: PromoterFunction[_T]
        ) -> PromoterFunction[_T]:
            for _type in types:
                self.add_promoter_for_type(_type, f)
            return f

        return decorator

    def prompt_str(
        self
    ) -> Callable[[SyncNoArgsCallback[str]], SyncNoArgsCallback[str]]:
        """A decorator for specifying an application's prompt."""

        def decorator(
            callback_func: SyncNoArgsCallback[str]
        ) -> SyncNoArgsCallback[str]:
            try:
                assert_sync_callback(callback_func)
            except InvalidCallbackTypeError as e:
                raise e

            self._prompt_callback = callback_func
            return callback_func

        return decorator

    def on_exit(
        self
    ) -> Callable[[AsyncNoArgsCallback[Any]], AsyncNoArgsCallback[Any]]:
        """A decorator for specifying a callback to be executed when the app exits.

        These callbacks will only be implicitly executed at the end of :method:`prompt`
        execution. Otherwise, the programmer must manually call
        :method:`run_on_init_callbacks`.

        """

        def decorator(
            callback_coro: AsyncNoArgsCallback[Any]
        ) -> AsyncNoArgsCallback[Any]:
            try:
                assert_async_callback(callback_coro)
            except InvalidCallbackTypeError as e:
                raise e

            self._on_exit_callbacks.append(callback_coro)
            return callback_coro

        return decorator

    def on_init(
        self
    ) -> Callable[[AsyncNoArgsCallback[Any]], AsyncNoArgsCallback[Any]]:
        """A decorator for specifying a callback to be executed when the prompt begins.

        These callbacks will only be implicitly executed at the beginning of
        :method:`prompt` execution. Otherwise, the programmer must manually call
        :method:`run_on_init_callbacks`.

        """

        def decorator(
            callback_coro: AsyncNoArgsCallback[Any]
        ) -> AsyncNoArgsCallback[Any]:
            try:
                assert_async_callback(callback_coro)
            except InvalidCallbackTypeError as e:
                raise e

            self._on_init_callbacks.append(callback_coro)
            return callback_coro

        return decorator

    async def run_async_callbacks(
        self,
        async_callbacks: Iterable[AsyncNoArgsCallback[_T]],
        *args: Any,
        **kwargs: Any
    ) -> List[_T]:
        """Run a collection of asynchronous callbacks with the specified arguments.

        Returns:
            The return value of each of the registered callbacks, in the order that
            they were registed.

        """
        wrapped_awaitable_callbacks = [
            self.call_as_current_app_async(async_callback, *args, **kwargs)
            for async_callback in async_callbacks
        ]

        return list(await asyncio.gather(*wrapped_awaitable_callbacks))

    async def run_on_exit_callbacks(
        self
    ) -> List[Any]:
        """Run all of the registered on-exit callbacks."""
        return await self.run_async_callbacks(self._on_exit_callbacks)

    async def run_on_init_callbacks(
        self
    ) -> List[Any]:
        """Run all of the registered on-init callbacks."""
        return await self.run_async_callbacks(self._on_init_callbacks)

    def call_as_current_app_sync(
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

    def print_exception_info(
        self,
        exc: Exception,
        unknown=False
    ) -> None:
        if (
            self._print_all_exception_tracebacks or
            (unknown and self._print_unknown_exception_tracebacks)
        ):
            if unknown:
                self.io.error('Unknown exception occurred:\n')
            else:
                self.io.error('Exception occurred:\n')

            tb = ''.join(traceback.format_exception(
                etype=type(exc),
                value=exc,
                tb=exc.__traceback__
            ))
            highlighted_tb = highlight(
                tb, Python3TracebackLexer(), TerminalFormatter()
            )
            self.io.ansi(highlighted_tb)
        else:
            self.io.error(str(exc))

    def print_command_suggestions(
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

        self.io.info('Perhaps you meant one of these:')
        for suggestion in suggestions:
            self.io.raw('    ', suggestion, sep='')

    def _prompt_callback_wrapper(
        self
    ) -> str:
        """A callback for getting the current page's prompt."""
        return self.call_as_current_app_sync(self._prompt_callback)

    def _default_prompt_callback(
        self
    ) -> str:
        return '> '

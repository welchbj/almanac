"""Decorators for customizing commands."""

from __future__ import annotations

import asyncio
import functools

from typing import (
    Any,
    Callable,
    cast,
    Coroutine,
    Iterable,
    List,
    Optional,
    Protocol,
    TYPE_CHECKING,
    TypeVar,
    Union
)

from prompt_toolkit.completion import Completer

from ..arguments import MutableArgument
from ..commands import CommandBase, FrozenCommand, MutableCommand
from ..completion import WordCompleter
from ..errors import (
    InvalidArgumentNameError,
    InvalidCallbackTypeError,
    NoSuchArgumentError,
    NoSuchCommandError
)
from ..parsing import Patterns
from ..types import CommandCoroutine

if TYPE_CHECKING:
    from .application import Application
    from .command_engine import CommandEngine

_T = TypeVar('_T', covariant=True)

CommandDecorator = Callable[[Union[MutableCommand, CommandCoroutine]], CommandBase]

# In the future, would like to make AsyncHookCallback a generic protocol-based type. In
# the meantime, we'll settle for the ambiguous return type of Any.
#
# Seems to depend on this issue:
# https://github.com/python/mypy/issues/5876
AsyncHookCallback = Callable[..., Coroutine[Any, Any, Any]]


class AsyncNoArgsCallback(Protocol[_T]):
    def __call__(self) -> Coroutine[Any, Any, _T]:
        ...


class SyncNoArgsCallback(Protocol[_T]):
    def __call__(self) -> _T:
        ...


def assert_sync_callback(
    candidate: Any
) -> None:
    """Assert that the candidate is a valid synchronous callback."""
    if not callable(candidate) or asyncio.iscoroutinefunction(candidate):
        raise InvalidCallbackTypeError(
            f'Invalid synchronous callback {candidate}'
        )


def assert_async_callback(
    candidate: Any
) -> None:
    """Assert that the candidate is a valid asynchronous."""
    if not asyncio.iscoroutinefunction(candidate):
        raise InvalidCallbackTypeError(
            f'Invalid asynchronous callback {candidate}'
        )


class ArgumentDecoratorProxy:
    """A simple proxy for providing argument-mutating decorators."""

    def __getattr__(
        self,
        argument_name: str
    ) -> Callable[..., CommandDecorator]:
        """Dynamically create decorators that mutate the desired argument."""

        def decorator(
            *,
            name: Optional[str] = None,
            description: Optional[str] = None,
            choices: Optional[Iterable[str]] = None,
            completers: Optional[Union[Completer, Iterable[Completer]]] = None,
            hidden: Optional[bool] = None
        ) -> CommandDecorator:

            def wrapped(
                command_or_coro: Union[MutableCommand, CommandCoroutine]
            ) -> MutableCommand:
                command: MutableCommand = MutableCommand.ensure_command(command_or_coro)

                try:
                    argument: MutableArgument = command[argument_name]
                except NoSuchArgumentError as e:
                    raise e

                if name is not None:
                    if not Patterns.is_valid_identifier(name):
                        raise InvalidArgumentNameError(f'Invalid identifier {name}')

                    argument.display_name = name

                if description is not None:
                    argument.description = description

                if choices is not None:
                    if isinstance(choices, str):
                        choice_list = [choices]
                    else:
                        choice_list = [x for x in choices]

                    argument.completers.append(WordCompleter(choice_list))

                if completers is not None:
                    if isinstance(completers, Completer):
                        argument.completers.append(completers)
                    else:
                        argument.completers.extend(completers)

                if hidden is not None:
                    argument.hidden = hidden

                return command

            return wrapped

        return decorator

    __getitem__ = __getattr__


class CommandDecoratorProxy:
    """A simple proxy for providing command-mutating decorators."""

    def __init__(
        self,
        app: Application
    ) -> None:
        self._app = app

    def register(
        self,
        *decorators: CommandDecorator
    ) -> CommandDecorator:
        """A decorator for registering a command on an application.

        This should always be the top-most (i.e., lowest line number) decorator in a
        stack on top of the coroutine you want to register as a command.

        Optionally, a series of other command- or argument-mutating decorators may be
        provided. This will result in a function being returned from this method that
        both applies any of these mutations and registers the command.

        """

        composed_decorator_func = self.compose(*decorators)

        def wrapped(
            command_or_coro: Union[MutableCommand, CommandCoroutine]
        ) -> FrozenCommand:
            command: MutableCommand = MutableCommand.ensure_command(command_or_coro)
            command = cast(MutableCommand, composed_decorator_func(command))

            frozen_command: FrozenCommand = command.freeze()
            self._app.command_engine.register(frozen_command)
            return frozen_command

        return wrapped

    def compose(
        self,
        *decorators: CommandDecorator
    ) -> CommandDecorator:
        """Compose several command decorators into one."""
        def _compose2(f, g):
            def wrapped(command_or_coro):
                return f(g(command_or_coro))
            return wrapped

        def _nop(command_or_coro):
            return command_or_coro

        return functools.reduce(_compose2, decorators, _nop)

    def __call__(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        aliases: Optional[Union[str, Iterable[str]]] = None
    ) -> CommandDecorator:
        """A decorator for mutating properties of a :class:`MutableCommand`."""
        def wrapped(
            command_or_coro: Union[MutableCommand, CommandCoroutine]
        ) -> MutableCommand:
            command: MutableCommand = MutableCommand.ensure_command(command_or_coro)

            if name is not None:
                if not Patterns.is_valid_identifier(name):
                    raise InvalidArgumentNameError(f'Invalid identifier {name}')

                command.name = name

            if description is not None:
                command.description = description

            if aliases is not None:
                command.add_alias(*aliases)

            return command

        return wrapped


class CommandHookDecoratorProxy:
    """A simple proxy for hooking actions before and after commands.

    Note:
        Command hook callbacks will be called with the same arguments as the command
        that they are hooking.

    """

    def __init__(
        self,
        app: Application
    ) -> None:
        self._app = app

    @property
    def command_engine(
        self
    ) -> CommandEngine:
        return self._app.command_engine

    def _resolved_commands(
        self,
        *command_names: str
    ) -> List[FrozenCommand]:
        nonexistent_command_names = [
            name for name in command_names
            if name not in self._app.command_engine.keys()
        ]

        if nonexistent_command_names:
            raise NoSuchCommandError(*nonexistent_command_names)

        return [self._app.command_engine[name] for name in command_names]

    def before(
        self,
        *command_names: str
    ) -> Callable[[AsyncHookCallback], AsyncHookCallback]:
        """A decorator for adding a callback to fire before commands execute."""
        frozen_commands = self._resolved_commands(*command_names)

        def decorator(
            hook_coro: AsyncHookCallback
        ) -> AsyncHookCallback:
            try:
                assert_async_callback(hook_coro)
            except InvalidCallbackTypeError as e:
                raise e

            for command in frozen_commands:
                self.command_engine.add_before_command_callback(command, hook_coro)
            return hook_coro

        return decorator

    def after(
        self,
        *command_names: str
    ) -> Callable[[AsyncHookCallback], AsyncHookCallback]:
        """A decorator for adding a callback to fire after commands execute."""
        frozen_commands = self._resolved_commands(*command_names)

        def decorator(
            hook_coro: AsyncHookCallback
        ) -> AsyncHookCallback:
            try:
                assert_async_callback(hook_coro)
            except InvalidCallbackTypeError as e:
                raise e

            for command in frozen_commands:
                self.command_engine.add_after_command_callback(command, hook_coro)
            return hook_coro

        return decorator

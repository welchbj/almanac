from __future__ import annotations

import functools

from typing import Callable, Iterable, Optional, TYPE_CHECKING, Union

from prompt_toolkit.completion import Completer

from ..arguments import MutableArgument
from ..commands import FrozenCommand, MutableCommand
from ..completion import WordCompleter
from ..errors import (
    InvalidArgumentNameError,
    NoSuchArgumentError,
)
from ..parsing import Patterns
from ..types import CommandCoroutine

if TYPE_CHECKING:
    from .application import Application


CommandMutatingDecorator = \
    Callable[[Union[MutableCommand, CommandCoroutine]], MutableCommand]

CommandFreezingDecorator = \
    Callable[[Union[MutableCommand, CommandCoroutine]], FrozenCommand]


class ArgumentDecoratorProxy:
    """A simple proxy for providing argument-mutating decorators."""

    def __getattr__(
        self,
        argument_name: str
    ) -> Callable[..., CommandMutatingDecorator]:
        """Dynamically create decorators that mutate the desired argument."""

        def decorator(
            *,
            name: Optional[str] = None,
            description: Optional[str] = None,
            choices: Optional[Iterable[str]] = None,
            completers: Optional[Union[Completer, Iterable[Completer]]] = None,
            hidden: Optional[bool] = None
        ) -> CommandMutatingDecorator:

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
        *decorators: CommandMutatingDecorator
    ) -> CommandFreezingDecorator:
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
            command = composed_decorator_func(command)

            frozen_command: FrozenCommand = command.freeze()
            self._app.command_engine.register(frozen_command)
            return frozen_command

        return wrapped

    def compose(
        self,
        *decorators: CommandMutatingDecorator
    ) -> CommandMutatingDecorator:
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
    ) -> CommandMutatingDecorator:
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
                if isinstance(aliases, str):
                    command.add_alias(aliases)
                else:
                    command.add_alias(*aliases)

            return command

        return wrapped

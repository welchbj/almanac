"""Decorators for customizing commands."""

from __future__ import annotations

from typing import Callable, Iterable, Optional, TYPE_CHECKING, Union

from prompt_toolkit.completion import Completer

from ..arguments import MutableArgument
from ..commands import CommandBase, FrozenCommand, MutableCommand
from ..errors import NoSuchArgumentError
from ..types import CommandCoroutine

CommandDecorator = Callable[[Union[MutableCommand, CommandCoroutine]], CommandBase]

if TYPE_CHECKING:
    from .application import Application


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
            completer: Optional[Completer] = None
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
                    argument.display_name = name

                if description is not None:
                    argument.description = description

                if completer is not None:
                    argument.completer = completer

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
        self
    ) -> CommandDecorator:
        """A decorator for registering a command on an application.

        This should always be the top-most (i.e., lowest line number) decorator in a
        stack on top of the coroutine you want to register as a command.

        """

        def wrapped(
            command_or_coro: Union[MutableCommand, CommandCoroutine]
        ) -> FrozenCommand:
            command: MutableCommand = MutableCommand.ensure_command(command_or_coro)
            frozen_command: FrozenCommand = command.freeze()
            self._app.command_engine.register(frozen_command)
            return frozen_command

        return wrapped

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
                command.name = name

            if description is not None:
                command.description = description

            if aliases is not None:
                command.add_alias(*aliases)

            return command

        return wrapped

"""Decorators for customizing commands."""

from typing import Callable, Optional, Union

from prompt_toolkit.completion import Completer

from ..commands import CommandBase, MutableCommand
from ..errors import NoSuchArgumentError
from ..types import CommandCoroutine

CommandDecorator = Callable[[Union[MutableCommand, CommandCoroutine]], CommandBase]


def argument(
    argument_name: str,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    completer: Optional[Completer] = None
) -> CommandDecorator:
    """Decorator for modifying the fields of a specific argument of a command."""

    def wrapped(
        command_or_coro: Union[MutableCommand, CommandCoroutine]
    ) -> MutableCommand:
        command: MutableCommand = MutableCommand.ensure_command(command_or_coro)

        # TODO: should we be explicitly checking for FrozenCommand?... only if
        #       app.command actually starts returning it

        try:
            argument = command[argument_name]
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


def name(
    argument_name: str,
    name: str
) -> CommandDecorator:
    """Shorthand decorator for specifying an argument's name."""
    return argument(argument_name, name=name)


def description(
    argument_name: str,
    description: str
) -> CommandDecorator:
    """Shorthand decorator for specifying an argument's description."""
    return argument(argument_name, description=description)


def completer(
    argument_name: str,
    completer: Completer
) -> CommandDecorator:
    """Shorthand decorator for specifying an argument's completer."""
    return argument(argument_name, completer=completer)

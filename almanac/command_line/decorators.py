"""Decorators for customizing commands."""

from typing import Callable, Optional, Union

from prompt_toolkit.completion import Completer

from .commands import MutableCommand
from .types import CommandCoroutine

CommandDecorator = Callable[[Union[MutableCommand, CommandCoroutine]], MutableCommand]


def argument(
    argument_name: str,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    completer: Optional[Completer] = None
) -> CommandDecorator:
    def wrapped(
        command_or_coro: Union[MutableCommand, CommandCoroutine]
    ) -> MutableCommand:
        command = MutableCommand.ensure_command(command_or_coro)

        # TODO: set appropriate attributes... including arguments

        return command
    return wrapped


def completer(
    argument_name: str,
    completer: Completer
) -> CommandDecorator:
    """Shorthand decorator for specifying an argument's completer."""
    return argument(argument_name, completer=completer)


# TODO: name + description decorators

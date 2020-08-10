from __future__ import annotations

from typing import Callable, List, TYPE_CHECKING, Union

from .assertions import assert_async_callback
from .exception_hook_dispatch_table import ExceptionHookDispatchTable
from .types import AsyncHookCallback
from ..errors import InvalidCallbackTypeError, NoSuchCommandError

if TYPE_CHECKING:
    from ..commands import FrozenCommand
    from ..core import Application, CommandEngine


class HookProxy:
    """A simple proxy for hooking events.

    Command hook callbacks will be called with the same arguments as the command that
    they are hooking.

    Exception hook callbacks will be called with the raised exception.

    """

    def __init__(
        self,
        app: Application
    ) -> None:
        self._app = app
        self._exc_hook_dispatch_table = ExceptionHookDispatchTable()

    @property
    def command_engine(
        self
    ) -> CommandEngine:
        return self._app.command_engine

    @property
    def exception(
        self
    ) -> ExceptionHookDispatchTable:
        """A decorator to add a callback to fire when a matching exception occurs."""
        return self._exc_hook_dispatch_table

    def before(
        self,
        *command_names: Union[str, FrozenCommand]
    ) -> Callable[[AsyncHookCallback], AsyncHookCallback]:
        """A decorator to add a callback to fire before commands execute."""
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
        *command_names: Union[str, FrozenCommand]
    ) -> Callable[[AsyncHookCallback], AsyncHookCallback]:
        """A decorator to add a callback to fire after commands execute."""
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

    def _resolved_commands(
        self,
        *commands: Union[str, FrozenCommand]
    ) -> List[FrozenCommand]:
        nonexistent_command_names = [
            name_or_cmd for name_or_cmd in commands
            if isinstance(name_or_cmd, str) and
            name_or_cmd not in self._app.command_engine.keys()
        ]

        if nonexistent_command_names:
            raise NoSuchCommandError(*nonexistent_command_names)

        return [
            self._app.command_engine[name_or_cmd] if isinstance(name_or_cmd, str)
            else name_or_cmd
            for name_or_cmd in commands
        ]

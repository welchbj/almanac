"""Exception hooks for builtin error types."""

from ..context import current_app
from ..errors import (
    BaseArgumentError,
    NoSuchCommandError
)


async def hook_EOFError(exc: EOFError):
    app = current_app()
    app.quit()


async def hook_NoSuchCommandError(exc: NoSuchCommandError):
    app = current_app()

    app.io.error(exc)
    for command_name in exc.names:
        app.print_command_suggestions(command_name)


async def hook_BaseArgumentError(exc: BaseArgumentError):
    app = current_app()
    # TODO: finer grained handling of descendant argument types
    app.io.error(exc)

# TODO: what else do we want to handle by default?

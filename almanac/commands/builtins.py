"""Implementation of builtin commands."""

from ..core import (
    Application)
from ..io import (
    AbstractIoContext)

from .types import (
    OptsType)


async def cd(
    app: Application,
    io: AbstractIoContext,
    opts: OptsType
) -> int:
    """Change directories.

    Usage:
        cd -
        cd <dest>

    """
    # TODO
    io.print_info('Called cd')
    return 0


async def help(
    app: Application,
    io: AbstractIoContext,
    opts: OptsType
) -> int:
    """Print help text about the current page or a command.

    Usage:
        help
        help <command>

    """
    # TODO
    io.print_info('Called help')
    return 0


async def ls(
    app: Application,
    io: AbstractIoContext,
    opts: OptsType
) -> int:
    """List files in a directory.

    Usage:
        ls
        ls <path>

    """
    # TODO
    io.print_info('Called ls')
    return 0


async def quit(
    app: Application,

    io: AbstractIoContext,
    opts: OptsType
) -> int:
    """Quit the application.

    Usage:
        quit

    """
    # TODO
    io.print_info('Called quit')
    return 0

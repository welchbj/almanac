"""Implementation of builtin commands."""

from ..core import (
    Application)
from ..io import (
    AbstractIoContext)

from .types import (
    OptsType)


def cd(
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


def ls(
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

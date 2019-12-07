"""Implementation of builtin commands."""

from ..core import (
    Application)

from .types import (
    OptsType)


def cd(
    app: Application,
    opts: OptsType
) -> int:
    """Change directories.

    Usage:
        cd -
        cd <dest>

    """
    # TODO
    print('Called cd')
    return 0


def ls(
    app: Application,
    opts: OptsType
) -> int:
    """List files in a directory.

    Usage:
        ls
        ls <path>

    """
    # TODO
    print('Called ls')
    return 0

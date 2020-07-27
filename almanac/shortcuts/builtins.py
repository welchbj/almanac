"""Implementation of builtin commands."""

from typing import Optional

from ..constants import ExitCodes
from ..core import current_app
from ..pages import PagePath


async def cd(path: Optional[PagePath] = None) -> int:
    """Change directories."""
    app = current_app()

    app.io.print_info('Called cd')
    app.io.print_info('path:', path)

    return ExitCodes.OK


async def help() -> int:
    """Print help text about the current page or a command."""
    app = current_app()
    app.io.print_info('Called help')
    return ExitCodes.OK


async def ls(path: Optional[PagePath] = None) -> int:
    """List files in a directory."""
    app = current_app()
    app.io.print_info('Called ls')
    return ExitCodes.OK


async def quit(exit_code: int = ExitCodes.OK) -> int:
    """Quit the application."""
    app = current_app()
    app.io.print_info('Quitting!')
    return app.quit(exit_code)

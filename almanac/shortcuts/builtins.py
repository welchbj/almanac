"""Implementation of builtin commands."""

from typing import Optional

from ..constants import ExitCodes
from ..pages import PagePath
from ..context import current_app


async def cd(path: PagePath) -> int:
    """Change directories."""
    app = current_app()

    if path == '-':
        app.page_navigator.back()
    else:
        app.page_navigator.change_directory(path)

    return ExitCodes.OK


async def help() -> int:
    """Print help text about the current page or a command."""
    app = current_app()
    app.io.print_info('Called help')
    return ExitCodes.OK


async def ls(path: Optional[PagePath] = None) -> int:
    """List files in a directory."""
    app = current_app()

    if path is None:
        path = app.page_navigator.explode('.')

    for child_page in app.page_navigator[path].children:
        app.io.print_raw(child_page.path)

    return ExitCodes.OK


async def quit() -> int:
    """Quit the application."""
    app = current_app()
    app.io.print_info('Quitting!')
    app.quit()
    return ExitCodes.OK

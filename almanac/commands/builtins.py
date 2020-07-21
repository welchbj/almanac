"""Implementation of builtin commands."""

from typing import Optional

from ..core import current_app


async def cd(path: Optional[str]) -> int:
    """Change directories."""
    app = current_app()
    app.io.print_info('Called cd')
    return 0


async def help() -> int:
    """Print help text about the current page or a command."""
    app = current_app()
    app.io.print_info('Called help')
    return 0


async def ls(path: Optional[str]) -> int:
    """List files in a directory."""
    app = current_app()
    app.io.print_info('Called ls')
    return 0


async def quit() -> int:
    """Quit the application."""
    app = current_app()
    app.io.print_info('Called quit')
    return 0

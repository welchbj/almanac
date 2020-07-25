"""Shortcuts for initializing a pre-built application."""

from .application import Application
from ..command_line.builtins import cd, help, ls, quit

# TODO: below will probably be decorators soon


def make_standard_app(
    with_pages: bool = True
) -> Application:
    """Instantiate and configure a standard application.

    When pages enabled, file-related commands will be registered on the returned
    :class:`Application` instance. Otherwise, only a few barebones commands are
    registered (quit, help, etc.).

    """
    app = Application()

    register_command = app.command()

    register_command(help)
    register_command(quit)

    if with_pages:
        register_command(cd)
        register_command(ls)

    return app

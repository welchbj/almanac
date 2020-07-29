"""Shortcuts for initializing a pre-built application."""

from .builtins import cd, help, ls, quit
from ..core import Application


def make_standard_app(
    with_pages: bool = True
) -> Application:
    """Instantiate and configure a standard application.

    When pages enabled, file-related commands will be registered on the returned
    :class:`Application` instance. Otherwise, only a few barebones commands are
    registered (quit, help, etc.).

    """
    app = Application()

    register_command = app.cmd.register()

    register_command(help)
    register_command(quit)

    if with_pages:
        register_command(cd)
        register_command(ls)

    return app

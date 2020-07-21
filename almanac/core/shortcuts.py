"""Shortcuts for initializing a pre-built application."""

from .application import Application
from ..commands.builtins import cd, help, ls, quit


def make_standard_app(
    with_pages: bool = True
) -> Application:
    """Instantiate and configure a standard application.

    When pages enabled, file-related commands will be registered on the returned
    :class:`Application` instance. Otherwise, only a few barebones commands are
    registered (quit, help, etc.).

    """
    app = Application()

    app.command(help)
    app.command(quit)

    if with_pages:
        app.command(cd)
        app.command(ls)

    return app

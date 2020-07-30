"""Shortcuts for initializing a pre-built application."""

from prompt_toolkit.styles import Style

from .builtins import cd, help, ls, quit
from ..completion import PagePathCompleter, WordCompleter
from ..core import Application
from ..pages import PagePath
from ..style import DARK_MODE_STYLE


def make_standard_app(
    with_completion: bool = True,
    with_pages: bool = True,
    with_style: bool = True,
    style: Style = DARK_MODE_STYLE
) -> Application:
    """Instantiate and configure a standard application.

    When pages enabled, file-related commands will be registered on the returned
    :class:`Application` instance. Otherwise, only a few barebones commands are
    registered (quit, help, etc.).

    """
    app = Application(
        with_completion=with_completion,
        with_style=with_style,
        style=style
    )

    app.add_completers_for_type(bool, WordCompleter(['True', 'False']))
    app.add_completers_for_type(PagePath, PagePathCompleter())

    register_command = app.cmd.register()

    register_command(help)
    register_command(quit)

    if with_pages:
        register_command(cd)
        register_command(ls)

    return app

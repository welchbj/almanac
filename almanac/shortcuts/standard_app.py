"""Shortcuts for initializing a pre-built application."""

from typing import Type

from prompt_toolkit.styles import Style

from .builtins import cd, help, ls, quit
from ..completion import PagePathCompleter, WordCompleter
from ..context import current_app
from ..core import Application
from ..io import AbstractIoContext, StandardConsoleIoContext
from ..pages import PagePath
from ..style import DARK_MODE_STYLE


def _current_page_prompt_str(
) -> str:
    app = current_app()
    return app.page_navigator.current_page.get_prompt()


def make_standard_app(
    *,
    with_completion: bool = True,
    with_pages: bool = True,
    with_style: bool = True,
    style: Style = DARK_MODE_STYLE,
    io_context_cls: Type[AbstractIoContext] = StandardConsoleIoContext,
    propagate_runtime_exceptions: bool = False
) -> Application:
    """Instantiate and configure a standard application.

    When pages enabled, file-related commands will be registered on the returned
    :class:`Application` instance. Otherwise, only a few barebones commands are
    registered (quit, help, etc.).

    """
    app = Application(
        with_completion=with_completion,
        with_style=with_style,
        style=style,
        io_context_cls=io_context_cls,
        propagate_runtime_exceptions=propagate_runtime_exceptions
    )

    app.add_completers_for_type(bool, WordCompleter(['True', 'False']))

    register_command = app.cmd.register()

    register_command(help)
    register_command(quit)

    if with_pages:
        app.add_completers_for_type(PagePath, PagePathCompleter())
        app.add_promoter_for_type(PagePath, PagePath)

        register_prompt_str = app.prompt_str()
        register_prompt_str(_current_page_prompt_str)

        register_command(cd)
        register_command(ls)

    return app

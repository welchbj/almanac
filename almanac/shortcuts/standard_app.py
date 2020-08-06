"""Shortcuts for initializing a pre-built application."""

from typing import Type

from prompt_toolkit.styles import Style

from .builtins import (
    back as builtin_back,
    cd as builtin_cd,
    forward as builtin_forward,
    help as builtin_help,
    ls as builtin_ls,
    pwd as builtin_pwd,
    quit as builtin_quit
)
from .exception_hooks import (
    hook_BaseArgumentError,
    hook_BasePageError,
    hook_NoSuchCommandError
)
from .promoters import promote_to_page_path
from ..completion import PagePathCompleter, WordCompleter
from ..context import current_app
from ..core import Application
from ..errors import (
    BaseArgumentError,
    BasePageError,
    NoSuchCommandError
)
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
    propagate_runtime_exceptions: bool = False,
    print_all_exception_tracebacks: bool = False,
    print_unknown_exception_tracebacks: bool = True
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
        propagate_runtime_exceptions=propagate_runtime_exceptions,
        print_all_exception_tracebacks=print_all_exception_tracebacks,
        print_unknown_exception_tracebacks=print_unknown_exception_tracebacks
    )

    app.add_completers_for_type(bool, WordCompleter(['True', 'False']))

    app.add_promoter_for_type(str, str)

    register_command = app.cmd.register()
    register_exc_hook = app.hook.exception.set_hook_for_exc_type

    register_command(builtin_help)
    register_command(builtin_quit)

    register_exc_hook(BaseArgumentError, hook_BaseArgumentError)
    register_exc_hook(NoSuchCommandError, hook_NoSuchCommandError)

    if with_pages:
        app.add_completers_for_type(PagePath, PagePathCompleter())
        app.add_promoter_for_type(PagePath, promote_to_page_path)

        register_prompt_str = app.prompt_str()
        register_prompt_str(_current_page_prompt_str)

        register_command(builtin_back)
        register_command(builtin_cd)
        register_command(builtin_forward)
        register_command(builtin_ls)
        register_command(builtin_pwd)

        register_exc_hook(BasePageError, hook_BasePageError)

    return app

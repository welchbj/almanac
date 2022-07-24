from typing import Type

from prompt_toolkit.styles import Style

from almanac.completion import PagePathCompleter, WordCompleter
from almanac.context import current_app
from almanac.core import Application
from almanac.errors import (
    BaseArgumentError,
    BasePageError,
    MissingArgumentsError,
    NoSuchArgumentError,
    NoSuchCommandError,
    TooManyPositionalArgumentsError,
    UnknownArgumentBindingError,
)
from almanac.io import AbstractIoContext, StandardConsoleIoContext
from almanac.pages import PagePath
from almanac.style import DARK_MODE_STYLE
from almanac.shortcuts.builtins import back as builtin_back
from almanac.shortcuts.builtins import cd as builtin_cd
from almanac.shortcuts.builtins import forward as builtin_forward
from almanac.shortcuts.builtins import help as builtin_help
from almanac.shortcuts.builtins import ls as builtin_ls
from almanac.shortcuts.builtins import pwd as builtin_pwd
from almanac.shortcuts.builtins import quit as builtin_quit
from almanac.shortcuts.exception_hooks import (
    hook_BaseArgumentError,
    hook_BasePageError,
    hook_MissingArgumentsError,
    hook_NoSuchArgumentError,
    hook_NoSuchCommandError,
    hook_TooManyPositionalArgumentsError,
    hook_UnknownArgumentBindingError,
)
from almanac.shortcuts.promoters import promote_to_page_path


def _current_page_prompt_str() -> str:
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
        print_unknown_exception_tracebacks=print_unknown_exception_tracebacks,
    )

    app.add_completers_for_type(bool, WordCompleter(["True", "False"]))

    app.add_promoter_for_type(str, str)

    add_command = app.cmd.register()
    add_exc_hook = app.hook.exception.set_hook_for_exc_type

    add_command(builtin_help)
    add_command(builtin_quit)

    add_exc_hook(BaseArgumentError, hook_BaseArgumentError)
    add_exc_hook(MissingArgumentsError, hook_MissingArgumentsError)
    add_exc_hook(NoSuchArgumentError, hook_NoSuchArgumentError)
    add_exc_hook(NoSuchCommandError, hook_NoSuchCommandError)
    add_exc_hook(TooManyPositionalArgumentsError, hook_TooManyPositionalArgumentsError)
    add_exc_hook(UnknownArgumentBindingError, hook_UnknownArgumentBindingError)

    if with_pages:
        app.add_completers_for_type(PagePath, PagePathCompleter())
        app.add_promoter_for_type(PagePath, promote_to_page_path)

        add_prompt_text = app.prompt_text()
        add_prompt_text(_current_page_prompt_str)

        add_command(builtin_back)
        add_command(builtin_cd)
        add_command(builtin_forward)
        add_command(builtin_ls)
        add_command(builtin_pwd)

        add_exc_hook(BasePageError, hook_BasePageError)

    return app

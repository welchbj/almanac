"""Shortcuts for initializing a pre-built application."""

from .application import (
    Application)
from ..commands.builtins import (
    cd,
    ls)


def make_standard_app(
) -> Application:
    """Instantiate and configure a standard application.

    This "standard" app will include the following:
        * All builtin commands registered on the app

    """
    app = Application()

    app.command(cd)
    app.command(ls)

    return app

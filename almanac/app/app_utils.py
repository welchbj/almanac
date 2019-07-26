"""Utilities for creating ``Application`` instances."""

from .application import (
    Application)
from ..commands import (
    BackCommand,
    CdCommand,
    EchoCommand,
    EncodeCommand,
    ForwardCommand,
    LsCommand,
    PwdCommand,
    SearchCommand)


def get_default_app() -> Application:
    """Get an application with the default configuration.

    TODO

    """
    app = Application()

    app.register_command(BackCommand())
    app.register_command(CdCommand())
    app.register_command(EchoCommand())
    app.register_command(EncodeCommand())
    app.register_command(ForwardCommand())
    app.register_command(LsCommand())
    app.register_command(PwdCommand())
    app.register_command(SearchCommand())

    return app

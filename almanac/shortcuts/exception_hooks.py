from almanac.context import current_app
from almanac.errors import (
    BaseArgumentError,
    BasePageError,
    MissingArgumentsError,
    NoSuchArgumentError,
    NoSuchCommandError,
    TooManyPositionalArgumentsError,
    UnknownArgumentBindingError,
)


async def hook_BaseArgumentError(exc: BaseArgumentError):
    app = current_app()
    app.io.error(exc)


async def hook_MissingArgumentsError(exc: MissingArgumentsError):
    app = current_app()
    app.io.error(exc)


async def hook_NoSuchArgumentError(exc: NoSuchArgumentError):
    app = current_app()
    app.io.error(exc)


async def hook_TooManyPositionalArgumentsError(exc: TooManyPositionalArgumentsError):
    app = current_app()
    app.io.error(exc)


async def hook_UnknownArgumentBindingError(exc: UnknownArgumentBindingError):
    app = current_app()
    app.io.error("Unable to bind arguments to command signature!")

    app.io.error("Signature:")
    app.io.error(f"    {exc.signature}")

    if exc.pos_args:
        app.io.error("Positional arguments:")
        for pos_arg in exc.pos_args:
            app.io.error(f"    {repr(pos_arg)}")

    if exc.kw_args:
        app.io.error("Keyword arguments:")
        for key, value in exc.kw_args.items():
            app.io.error(f"    {key}={repr(value)}")


async def hook_BasePageError(exc: BasePageError):
    app = current_app()
    app.io.error(exc)


async def hook_NoSuchCommandError(exc: NoSuchCommandError):
    app = current_app()

    app.io.error(exc)
    for command_name in exc.names:
        app.print_command_suggestions(command_name)

from ..constants import ExitCodes
from ..pages import PagePath, PagePathLike
from ..context import current_app
from ..core import ArgumentDecoratorProxy

_arg = ArgumentDecoratorProxy()


@_arg.path(description="The path to change into.")
async def cd(path: PagePath) -> int:
    """Change directories."""
    app = current_app()

    app.page_navigator.change_directory(path)

    return ExitCodes.OK


async def help() -> int:
    """Print help text about the current page or a command."""
    app = current_app()

    # XXX
    app.io.info("Called help")

    return ExitCodes.OK


@_arg.path(description="The path whose contents to list.")
async def ls(path: PagePathLike = ".") -> int:
    """List files in a directory."""
    app = current_app()

    for child_page in app.page_navigator[path].children:
        app.io.raw(child_page.path)

    return ExitCodes.OK


async def back() -> int:
    """Change to the previous directory in the page navigation history."""
    app = current_app()

    app.page_navigator.back()

    return ExitCodes.OK


async def forward() -> int:
    """Change to the next directory in the page navigation history."""
    app = current_app()

    app.page_navigator.forward()

    return ExitCodes.OK


async def pwd() -> int:
    """Print the current directory."""
    app = current_app()

    app.io.raw(app.current_path)

    return ExitCodes.OK


async def quit() -> int:
    """Quit the application."""
    app = current_app()

    app.io.info("Quitting!")
    app.quit()

    return ExitCodes.OK

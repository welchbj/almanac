from __future__ import annotations

from contextvars import ContextVar
from typing import Optional, TYPE_CHECKING

from ..errors import NoActiveApplicationError

if TYPE_CHECKING:
    from ..core import Application


_current_app: ContextVar[Optional[Application]] = ContextVar("_current_app")


def set_current_app(app: Application) -> None:
    """Set the current application."""
    _current_app.set(app)


def current_app() -> Application:
    """Get the currently running application.

    Raises:
        :class:`NoActiveApplicationError`: If this function is called when no
            application is running.

    """
    app = _current_app.get(None)
    if app is None:
        raise NoActiveApplicationError(
            "Attempted to get the current application via `current_app` when no "
            "application is running."
        )

    return app

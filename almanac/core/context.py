"""Context helpers for managing multiple applications."""

from __future__ import annotations

from asyncio import Lock
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Optional, TYPE_CHECKING

from ..errors import NoActiveApplicationError

if TYPE_CHECKING:
    from ..core import Application


_current_app: ContextVar[Optional[Application]] = ContextVar('_current_app')
_current_app_lock = Lock()


@asynccontextmanager
async def current_app_lock():
    async with _current_app_lock:
        yield


def set_current_app(
    app: Application
) -> None:
    """Set the current application.

    The caller must acquire the current application lock (via :func:`current_app_lock`
    for the duration that he or she desires to mark the current application

    """
    _current_app.set(app)


def current_app(
) -> Application:
    """Get the currently running application.

    Raises:
        :class:`NoActiveApplicationError`: If this function is called when no
            application is running.

    """
    app = _current_app.get(None)
    if app is None:
        raise NoActiveApplicationError(
            'Attempted to get the current application via `current_app` when no '
            'application is running.'
        )

    return app

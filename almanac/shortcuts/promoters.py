from typing import Any

from ..context import current_app
from ..pages import PagePath


def promote_to_page_path(
    raw_path: Any
) -> PagePath:
    """Attempt to promote an argument into a page path.

    This promoter will attempt to explode the specified argument into an absolute
    path. As such, any exceptions from :py:meth:`PageNavigator.explode` can also be
    raised from this function.

    """
    app = current_app()
    abs_path = app.page_navigator.explode(str(raw_path))
    return PagePath(abs_path)

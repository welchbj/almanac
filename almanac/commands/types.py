"""Additional type definitons."""

from typing import (
    Any,
    Callable,
    Dict,
    TYPE_CHECKING)

if TYPE_CHECKING:
    from ..application import (  # noqa
        Application)


OptsType = Dict[str, Any]
CommandCallable = Callable[['Application', OptsType], int]

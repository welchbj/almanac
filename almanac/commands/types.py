"""Additional type definitons."""

from typing import (
    Any,
    Coroutine,
    Callable,
    Dict,
    TYPE_CHECKING)

from ..io import (
    AbstractIoContext)

if TYPE_CHECKING:
    from ..application import (  # noqa
        Application)


OptsType = Dict[str, Any]
CommandCallable = Callable[
    ['Application', AbstractIoContext, OptsType],
    Coroutine[Any, Any, int]]

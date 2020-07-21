"""Additional type definitons."""

from typing import Any, Coroutine, Callable


CommandCallable = Callable[..., Coroutine[Any, Any, int]]
